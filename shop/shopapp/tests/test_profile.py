from django.test import TestCase, Client
from django.urls import reverse
from ..models import User
from rest_framework_simplejwt.tokens import RefreshToken
import json
import logging

logger = logging.getLogger(__name__)

class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Получаем токены
        refresh = RefreshToken.for_user(self.user)
        
        # Устанавливаем cookies
        self.client.cookies['access_token'] = str(refresh.access_token)
        self.client.cookies['refresh_token'] = str(refresh)
        
        # Устанавливаем заголовок авторизации
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {str(refresh.access_token)}'
        
        self.profile_url = '/shopapp/api/profile/'  # Исправленный URL

    def test_get_profile_authenticated(self):
        try:
            response = self.client.get(self.profile_url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertEqual(data['username'], 'testuser')
            self.assertEqual(data['email'], 'test@example.com')
            self.assertEqual(data['first_name'], 'Test')
            self.assertEqual(data['last_name'], 'User')
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise

    def test_get_profile_unauthenticated(self):
        """Тест получения данных профиля неавторизованным пользователем"""
        self.client.logout()
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_update_profile(self):
        try:
            update_data = {
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@example.com'
            }
            
            response = self.client.put(
                self.profile_url,
                data=json.dumps(update_data),
                content_type='application/json'
            )
            logger.info(f"Response content: {response.content}")
            
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise

    def test_update_profile_invalid_email(self):
        try:
            update_data = {
                'email': 'invalid-email'
            }
            
            response = self.client.put(
                self.profile_url,
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn('error', data)
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise

    def test_delete_profile(self):
        response = self.client.delete(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_update_profile_duplicate_email(self):
        try:
            # Создаем второго пользователя
            User.objects.create_user(
                username='another',
                email='another@example.com',
                password='pass123'
            )
            
            update_data = {
                'email': 'another@example.com'
            }
            
            response = self.client.put(
                self.profile_url,
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertEqual(data['error'], 'Пользователь с таким email уже существует')
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise 