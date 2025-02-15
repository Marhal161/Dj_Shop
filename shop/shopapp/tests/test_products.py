from django.test import TestCase, Client
from django.urls import reverse
from ..models import Product, Category, ProductScreenshot, User, Review
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import shutil
from django.conf import settings

class ProductTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Game',
            description='Test Description',
            price=99.99,
            available_quantity=10
        )
        self.product.categories.add(self.category)
        
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

        # Создаем временную директорию для тестовых медиа-файлов
        self.test_media_dir = os.path.join(settings.MEDIA_ROOT, 'test_screenshots')
        os.makedirs(self.test_media_dir, exist_ok=True)

        # Сохраняем список существующих файлов до теста
        self.existing_files = set()
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                self.existing_files.add(os.path.join(root, file))

    def tearDown(self):
        """Очистка после тестов"""
        # Получаем список всех файлов после теста
        current_files = set()
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                current_files.add(os.path.join(root, file))

        # Удаляем только новые файлы (тестовые)
        files_to_remove = current_files - self.existing_files
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)

        # Удаляем только пустые тестовые директории
        if os.path.exists(self.test_media_dir):
            try:
                os.rmdir(self.test_media_dir)  # Удалит директорию только если она пуста
            except OSError:
                pass  # Игнорируем ошибку, если директория не пуста

    def test_product_detail_view(self):
        response = self.client.get(reverse('game_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)  # Редирект на auth_page из-за декоратора

    def test_product_list_view(self):
        response = self.client.get(reverse('game_view'))
        self.assertEqual(response.status_code, 302)  # Редирект на auth_page из-за декоратора

    def test_product_screenshot_upload(self):
        # Создаем тестовое изображение во временной директории
        image_path = os.path.join(self.test_media_dir, "test.jpg")
        with open(image_path, 'wb') as f:
            f.write(b"file_content")

        # Создаем файл для загрузки
        with open(image_path, 'rb') as f:
            image = SimpleUploadedFile(
                "test.jpg",
                f.read(),
                content_type="image/jpeg"
            )
        
        # Создаем скриншот
        screenshot = ProductScreenshot.objects.create(
            product=self.product,
            image=image,
            order=0
        )

        # Проверяем, что скриншот создан
        self.assertTrue(ProductScreenshot.objects.filter(product=self.product).exists())
        
        # Проверяем, что файл существует
        self.assertTrue(os.path.exists(screenshot.image.path))

        # Удаляем временный файл
        if os.path.exists(image_path):
            os.remove(image_path) 