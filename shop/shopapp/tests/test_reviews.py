from django.test import TestCase, Client
from shopapp.models import Product, User, Review
from rest_framework_simplejwt.tokens import RefreshToken
import json
import logging

logger = logging.getLogger(__name__)

class ReviewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        logger.debug(f"Created test user: {self.user}")
        # Создаем тестовый продукт
        self.product = Product.objects.create(
            name='Test Game',
            description='Test Description',
            price=99.99,
            available_quantity=10
        )
        logger.debug(f"Created test product: {self.product}")
        self.review_url = '/shopapp/api/review/'
        
        # Создаем токены напрямую
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)
        
        # Устанавливаем токены в куки
        self.client.cookies['access_token'] = self.access_token
        self.client.cookies['refresh_token'] = self.refresh_token
        logger.debug("Set up tokens in cookies")

    def test_create_review(self):
        review_data = {
            'product': self.product.id,
            'rating': 5,
            'comment': 'Great game!'
        }
        logger.debug(f"Sending review data: {review_data}")
        
        response = self.client.post(
            self.review_url,
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response content: {response.content}")
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Review.objects.filter(
            product=self.product,
            user=self.user,
            rating=5
        ).exists())

    def test_get_reviews(self):
        # Создаем тестовый отзыв
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Great game!'
        )
        logger.debug(f"Created test review: {review}")
        
        # Получаем отзывы для продукта
        response = self.client.get(
            f'{self.review_url}?product_id={self.product.id}'
        )
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response content: {response.content}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['reviews']), 1)

    def test_invalid_review_data(self):
        # Отправляем невалидные данные
        invalid_data = {
            'product': self.product.id,
            'rating': 6,  # Невалидный рейтинг
            'comment': ''
        }
        logger.debug(f"Sending invalid review data: {invalid_data}")
        
        response = self.client.post(
            self.review_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response content: {response.content}")
        
        self.assertEqual(response.status_code, 400) 