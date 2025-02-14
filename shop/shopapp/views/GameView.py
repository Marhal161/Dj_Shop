from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..models import Product
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

class GameView(View):
    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def get(self, request):
        try:
            games = Product.objects.all()  # Извлекаем все игры
            print(f"Количество игр: {games.count()}")  # Отладочный вывод

            # Выводим пути к изображениям для отладки
            for game in games:
                for screenshot in game.screenshots.all():
                    print(f"Image path: {screenshot.image.path}")

            # Передаем данные о играх в контекст шаблона
            return render(request, 'main.html', {'games': games})

        except Exception as e:
            logger.error(f"Error fetching games: {str(e)}")
            return render(request, 'error.html', {'error': str(e)}, status=500)
