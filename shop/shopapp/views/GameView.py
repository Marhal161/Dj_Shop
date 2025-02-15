from django.shortcuts import render, get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..models import Product, ProductScreenshot
import logging
from ..decorators import check_auth_tokens
from rest_framework.views import APIView

# Настройка логгера
logger = logging.getLogger(__name__)

@method_decorator(check_auth_tokens, name='get')  # Защищаем GET-метод
class GameView(APIView):
    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def get(self, request):
        try:
            games = Product.objects.all()  # Извлекаем все игры

            # Проверяем наличие токенов в cookies
            access_token = request.COOKIES.get('access_token')
            refresh_token = request.COOKIES.get('refresh_token')
            
            # Создаем контекст с информацией о пользователе
            context = {
                'games': games,
                'user': request.user,
                'is_authenticated': bool(access_token and refresh_token)  # Проверяем наличие обоих токенов
            }

            return render(request, 'main.html', context)

        except Exception as e:
            logger.error(f"Error fetching games: {str(e)}")
            return render(request, 'error.html', {'error': str(e)}, status=500)


@check_auth_tokens
def game_detail(request, game_id):
    game = get_object_or_404(Product, id=game_id)
    screenshots = game.screenshots.all()
    
    # Добавляем отладочную информацию
    print("Screenshots in view:", screenshots)
    for screenshot in screenshots:
        print(f"Screenshot path: {screenshot.image.path}")
        print(f"Screenshot URL: {screenshot.image.url}")
    
    context = {
        'title': game.name,
        'description': game.description,
        'price': game.price,
        'quantity': game.available_quantity,
        'categories': game.categories.all(),
        'screenshots': screenshots,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'game_detail.html', context)
