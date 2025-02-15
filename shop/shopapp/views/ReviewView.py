import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from ..models import Review, User, Product
from ..serializers.ReviewSerializer import ReviewSerializer
from ..decorators import check_auth_tokens
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import render
# Настройка логгера
logger = logging.getLogger(__name__)

@method_decorator(check_auth_tokens, name='get')  # Защищаем GET-метод

class ReviewView(APIView):
    
    @method_decorator(check_auth_tokens)
    def get(self, request):
        try:
            logger.debug(f"GET request params: {request.GET}")
            # Получаем product_id из параметров запроса
            product_id = request.GET.get('product_id')
            
            if not product_id:
                return Response(
                    {'error': 'Product ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Получаем все отзывы для конкретного продукта
            reviews = Review.objects.filter(product_id=product_id).select_related('user').order_by('-created_at')
            logger.debug(f"Found {reviews.count()} reviews")
            
            # Сериализуем отзывы
            serializer = ReviewSerializer(reviews, many=True)

            return Response({
                'success': True,
                'reviews': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in GET reviews: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(check_auth_tokens)
    def post(self, request):
        try:
            logger.debug(f"POST request data: {request.data}")
            # Получаем пользователя из токена
            access_token = request.COOKIES.get('access_token')
            token = AccessToken(access_token)
            user_id = token.payload.get('user_id')
            
            logger.debug(f"User ID from token: {user_id}")
            user = User.objects.get(id=user_id)
            logger.debug(f"Found user: {user}")

            # Создаем сериализатор с данными и контекстом
            serializer = ReviewSerializer(data=request.data, context={'user': user})
            
            if serializer.is_valid():
                logger.debug(f"Serializer is valid: {serializer.validated_data}")
                review = serializer.save()
                logger.debug(f"Review saved: {review}")
                return Response({
                    'success': True,
                    'review': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error in POST review: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
