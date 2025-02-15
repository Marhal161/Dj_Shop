from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from ..models import User, BalanceTransaction
from rest_framework_simplejwt.tokens import RefreshToken
import json
import logging

logger = logging.getLogger(__name__)

class BalanceViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            balance=Decimal('0.00')
        )
        
        # Получаем токены
        refresh = RefreshToken.for_user(self.user)
        
        # Устанавливаем cookies
        self.client.cookies['access_token'] = str(refresh.access_token)
        self.client.cookies['refresh_token'] = str(refresh)
        
        # Устанавливаем заголовок авторизации
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {str(refresh.access_token)}'
        
        self.balance_url = '/shopapp/api/profile/balance/'  # Исправленный URL

    def test_deposit_balance(self):
        try:
            deposit_data = {
                'amount': '100.00'
            }
            
            response = self.client.post(
                self.balance_url,
                data=json.dumps(deposit_data),
                content_type='application/json'
            )
            logger.info(f"Response content: {response.content}")
            
            self.assertEqual(response.status_code, 200)
            
            self.user.refresh_from_db()
            self.assertEqual(float(self.user.balance), 100.00)
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise

    def test_deposit_negative_amount(self):
        """Тест пополнения отрицательной суммой"""
        deposit_data = {
            'amount': -50.00
        }
        
        response = self.client.post(
            self.balance_url,
            data=json.dumps(deposit_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Проверяем, что баланс не изменился
        self.user.refresh_from_db()
        self.assertEqual(float(self.user.balance), 0.00)

    def test_deposit_zero_amount(self):
        """Тест пополнения нулевой суммой"""
        deposit_data = {
            'amount': 0.00
        }
        
        response = self.client.post(
            self.balance_url,
            data=json.dumps(deposit_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)

    def test_deposit_unauthenticated(self):
        """Тест пополнения баланса неавторизованным пользователем"""
        self.client.logout()
        
        deposit_data = {
            'amount': 100.00
        }
        
        response = self.client.post(
            self.balance_url,
            data=json.dumps(deposit_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_multiple_deposits(self):
        """Тест множественных пополнений баланса"""
        deposits = [100.00, 50.00, 75.00]
        
        for amount in deposits:
            response = self.client.post(
                self.balance_url,
                data=json.dumps({'amount': amount}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        # Проверяем итоговый баланс
        self.user.refresh_from_db()
        self.assertEqual(float(self.user.balance), sum(deposits))
        
        # Проверяем количество транзакций
        self.assertEqual(BalanceTransaction.objects.count(), len(deposits))

    def test_deposit_decimal_precision(self):
        """Тест точности десятичных чисел при пополнении"""
        deposit_data = {
            'amount': 100.99
        }
        
        response = self.client.post(
            self.balance_url,
            data=json.dumps(deposit_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.user.refresh_from_db()
        self.assertEqual(float(self.user.balance), 100.99) 