from django.shortcuts import render, get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..models import Product, ProductScreenshot, Category, Product
from django.db.models import Count, Q
import logging
from ..decorators import check_auth_tokens
from rest_framework.views import APIView
from django.conf import settings
from random import sample
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.core.management import call_command

# Настройка логгера
logger = logging.getLogger(__name__)

# Добавим функцию для проверки и создания тестовых данных
def ensure_test_data():
    if Product.objects.count() == 0:
        logger.info("No products found, creating test data...")
        try:
            # Создаем категории если их нет
            if Category.objects.count() == 0:
                Category.objects.create(name="Action")
                Category.objects.create(name="RPG")
                Category.objects.create(name="Strategy")

            # Создаем тестовые продукты
            action = Category.objects.get(name="Action")
            Product.objects.create(
                name="Test Game 1",
                description="Test description 1",
                price=999.99,
                available_quantity=10
            ).categories.add(action)

            Product.objects.create(
                name="Test Game 2",
                description="Test description 2",
                price=1999.99,
                available_quantity=5
            ).categories.add(action)

            logger.info("Test data created successfully")
        except Exception as e:
            logger.error(f"Error creating test data: {str(e)}")

@method_decorator(check_auth_tokens, name='get')  # Защищаем GET-метод
class GameView(APIView):
    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def get(self, request):
        try:
            games = Product.objects.all()
            # Получаем только топ-5 категорий
            categories = Category.objects.annotate(
                game_count=Count('products')
            ).order_by('-game_count')[:5]

            categories_with_images = []
            for category in categories:
                # Получаем все игры категории
                category_games = category.products.all()
                sample_size = min(3, category_games.count())
                random_games = sample(list(category_games), sample_size)
                
                image_urls = []
                for game in random_games:
                    if game.screenshots.exists():
                        image_urls.append(game.screenshots.first().image.url)
                
                categories_with_images.append({
                    'id': category.id,  # Добавляем ID категории
                    'name': category.name,
                    'count': category.game_count,
                    'image_urls': image_urls
                })
            
            # Проверяем наличие токенов в cookies
            access_token = request.COOKIES.get('access_token')
            refresh_token = request.COOKIES.get('refresh_token')
            
            context = {
                'games': games,
                'categories': categories_with_images,
                'user': request.user,
                'is_authenticated': bool(access_token and refresh_token)
            }

            return render(request, 'main.html', context)

        except Exception as e:
            logger.error(f"Error fetching games: {str(e)}")
            return render(request, 'error.html', {'error': str(e)}, status=500)


@check_auth_tokens
def game_detail(request, game_id):
    game = get_object_or_404(Product, id=game_id)
    screenshots = game.screenshots.all()
    
    context = {
        'game': game,  # Добавляем всю игру в контекст
        'title': game.name,
        'description': game.description,
        'price': game.price,
        'quantity': game.available_quantity,
        'categories': game.categories.all(),
        'screenshots': screenshots,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'game_detail.html', context)

@method_decorator(check_auth_tokens, name='get')
class GamesListView(View):
    def get(self, request):
        # Получаем параметры фильтрации
        category = request.GET.get('category')
        # Проверяем, что category является числом и не пустой
        categories = [category] if category and category.isdigit() else request.GET.getlist('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        sort = request.GET.get('sort', 'name')

        # Базовый QuerySet
        games = Product.objects.all()

        # Применяем фильтры только если есть валидные категории
        if categories and all(cat.isdigit() for cat in categories):
            games = games.filter(categories__id__in=categories)

        if min_price:
            games = games.filter(price__gte=min_price)

        if max_price:
            games = games.filter(price__lte=max_price)

        # Применяем сортировку
        if sort == 'price_asc':
            games = games.order_by('price')
        elif sort == 'price_desc':
            games = games.order_by('-price')
        elif sort == 'newest':
            games = games.order_by('-created_at')
        else:  # sort == 'name'
            games = games.order_by('name')

        # Получаем все категории для фильтра
        all_categories = Category.objects.all()

        context = {
            'games': games,
            'categories': all_categories,
            'selected_categories': categories,
            'min_price': min_price,
            'max_price': max_price,
            'sort': sort,
            'is_authenticated': request.user.is_authenticated,
        }

        return render(request, 'games.html', context)

@api_view(['GET'])
def games_api(request):
    try:
        # Получаем параметры фильтрации из запроса
        search_query = request.GET.get('search', '')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        sort_by = request.GET.get('sort', 'name')
        ratings = request.GET.get('rating', '').split(',')
        categories = request.GET.get('categories', '').split(',')
        
        # Начинаем с полного набора игр
        games = Product.objects.all()
        
        # Добавляем отладочную информацию
        logger.info(f"Initial games count: {games.count()}")
        
        # Применяем поиск по названию
        if search_query:
            games = games.filter(name__icontains=search_query)
            logger.info(f"After search filter: {games.count()} games")
        
        # Фильтрация по цене
        if min_price:
            games = games.filter(price__gte=float(min_price))
            logger.info(f"After min_price filter: {games.count()} games")
        if max_price:
            games = games.filter(price__lte=float(max_price))
            logger.info(f"After max_price filter: {games.count()} games")
            
        # Фильтрация по рейтингу
        if ratings and ratings[0]:
            filtered_games = []
            for game in games:
                game_rating = game.get_rating()
                if game_rating is not None:
                    for rating in ratings:
                        try:
                            if float(rating) == game_rating:
                                filtered_games.append(game.id)
                                break
                        except ValueError:
                            continue
            games = games.filter(id__in=filtered_games)
            logger.info(f"After rating filter: {games.count()} games")
            
        # Фильтрация по категориям
        if categories and categories[0]:
            category_ids = [cat for cat in categories if cat.isdigit()]
            if category_ids:
                games = games.filter(categories__id__in=category_ids)
                logger.info(f"After categories filter: {games.count()} games")
            
        # Сортировка
        if sort_by == 'price_asc':
            games = games.order_by('price')
        elif sort_by == 'price_desc':
            games = games.order_by('-price')
        elif sort_by == 'newest':
            games = games.order_by('-created_at')
        else:  # по умолчанию сортировка по названию
            games = games.order_by('name')
            
        # Преобразуем QuerySet в список словарей
        games_data = [{
            'id': game.id,
            'name': game.name,
            'description': game.description,
            'price': float(game.price),
            'rating': game.get_rating(),  # Используем метод для получения рейтинга
            'screenshot_url': game.screenshots.first().image.url if game.screenshots.exists() else None,
            'categories': [{'id': cat.id, 'name': cat.name} for cat in game.categories.all()],
            'quantity': game.available_quantity
        } for game in games]
        
        logger.info(f"Final games_data length: {len(games_data)}")
        
        return JsonResponse({'games': games_data})
        
    except Exception as e:
        logger.error(f"Error in games_api: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def categories_api(request):
    try:
        categories = Category.objects.all()
        categories_data = [{'id': cat.id, 'name': cat.name} for cat in categories]
        return JsonResponse({'categories': categories_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
