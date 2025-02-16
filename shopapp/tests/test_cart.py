from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse

class CartTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Создаем тестового пользователя
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        # Авторизуем пользователя
        self.client.force_authenticate(user=self.user)
        
        # Создаем тестовый продукт
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00
        ) 