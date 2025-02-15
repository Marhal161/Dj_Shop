from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import User, BalanceTransaction
from ..decorators import check_auth_tokens
from django.utils.decorators import method_decorator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import logging
from ..serializers.BalanceSerializer     import BalanceTransactionSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class ProfileView(APIView):
    @method_decorator(check_auth_tokens)
    def get(self, request):
        """Получение данных профиля"""
        try:
            # Получаем токен из cookies
            access_token = request.COOKIES.get('access_token')
            if not access_token:
                return Response(
                    {'error': 'Не найден токен доступа'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Получаем пользователя из токена
            token = AccessToken(access_token)
            User = get_user_model()
            user = User.objects.get(id=token['user_id'])

            profile_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'balance': float(user.balance)
            }
            return Response(profile_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Ошибка при получении профиля: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении данных профиля'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @method_decorator(check_auth_tokens)
    def put(self, request):
        """Обновление данных профиля"""
        try:
            user = request.user
            data = request.data

            # Валидация email
            if 'email' in data:
                try:
                    validate_email(data['email'])
                except ValidationError:
                    return Response(
                        {'error': 'Некорректный формат email'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Проверка на существующий email
                if User.objects.exclude(id=user.id).filter(email=data['email']).exists():
                    return Response(
                        {'error': 'Пользователь с таким email уже существует'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Обновление полей
            allowed_fields = ['first_name', 'last_name', 'email']
            for field in allowed_fields:
                if field in data:
                    setattr(user, field, data[field])

            try:
                user.save()
            except Exception as e:
                logger.error(f"Ошибка при сохранении пользователя: {str(e)}")
                return Response(
                    {'error': 'Ошибка при сохранении данных'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {'message': 'Профиль успешно обновлен'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Ошибка при обновлении профиля: {str(e)}")
            return Response(
                {'error': 'Ошибка при обновлении профиля'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @method_decorator(check_auth_tokens)
    def delete(self, request):
        """Удаление профиля"""
        try:
            user = request.user
            user.delete()
            return Response(
                {'message': 'Профиль успешно удален'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Ошибка при удалении профиля: {str(e)}")
            return Response(
                {'error': 'Ошибка при удалении профиля'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProfileBalanceView(APIView):
    @method_decorator(check_auth_tokens)
    def post(self, request):
        """Пополнение баланса"""
        try:
            serializer = BalanceTransactionSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                transaction = serializer.save()
                return Response({
                    'message': 'Баланс успешно пополнен',
                    'new_balance': float(request.user.balance),
                    'transaction': BalanceTransactionSerializer(transaction).data
                }, status=status.HTTP_200_OK)
            
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Ошибка при пополнении баланса: {str(e)}")
            return Response(
                {'error': 'Ошибка при пополнении баланса'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProfileBalanceTransactionsView(APIView):
    @method_decorator(check_auth_tokens)
    def get(self, request):
        """Получение истории транзакций"""
        try:
            transactions = BalanceTransaction.objects.filter(
                user=request.user
            ).order_by('-created_at')[:10]  # Получаем последние 10 транзакций
            
            serializer = BalanceTransactionSerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Ошибка при получении истории транзакций: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении истории транзакций'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
