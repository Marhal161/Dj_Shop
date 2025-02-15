from django.test import TestCase, Client
from shopapp.models import User, Product
from rest_framework_simplejwt.tokens import RefreshToken

class DecoratorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.product = Product.objects.create(
            name='Test Game',
            description='Test Description',
            price=99.99,
            available_quantity=10
        )
        self.protected_url = f'/shopapp/game/{self.product.id}/'
        self.auth_url = '/shopapp/auth/'  # Исправлен путь для редиректа

    def test_no_tokens(self):
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.auth_url)  # Теперь должно соответствовать

    def test_valid_tokens(self):
        # Создаем токены
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        # Устанавливаем куки
        self.client.cookies['access_token'] = access_token
        self.client.cookies['refresh_token'] = str(refresh)

        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, 200)

    def test_invalid_token(self):
        self.client.cookies['access_token'] = 'invalid_token'
        self.client.cookies['refresh_token'] = 'invalid_refresh_token'

        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.auth_url)  # Теперь должно соответствовать 