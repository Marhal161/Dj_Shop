from django.test import TestCase, Client
from django.urls import reverse
from shopapp.models import User
import json

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = '/shopapp/api/register/'
        self.login_url = '/shopapp/api/login/'
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_registration(self):
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
        self.assertTrue('access_token' in response.cookies)
        self.assertTrue('refresh_token' in response.cookies)

    def test_user_login(self):
        # Создаем пользователя
        User.objects.create_user(
            username='test',
            email=self.user_data['email'],
            password=self.user_data['password']
        )

        # Пытаемся залогиниться
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('access_token' in response.cookies)
        self.assertTrue('refresh_token' in response.cookies)

    def test_invalid_login(self):
        login_data = {
            'email': 'wrong@example.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401) 