from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
try:
    from rest_framework_simplejwt.tokens import RefreshToken
except ImportError:
    raise ImportError(
        "Не удалось импортировать RefreshToken. Убедитесь, что djangorestframework-simplejwt установлен корректно."
    )

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        
    def test_login(self):
        # Создаем тестового пользователя
        user = self.User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        user.is_active = True
        user.save()
        
        # Тестируем логин
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'testuser', 'password': 'testpass123'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_register(self):
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'test@example.com'
        }
        response = self.client.post(
            reverse('register_api'),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 201) 