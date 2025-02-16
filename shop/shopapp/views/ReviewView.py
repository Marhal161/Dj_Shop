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
            reviews_data = [{
                'id': review.id,
                'user': review.user.get_full_name() or review.user.username,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at,
                'is_owner': review.is_owner(request.user)
            } for review in reviews]

            return Response({
                'success': True,
                'reviews': reviews_data
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
            # Получаем данные из запроса
            product_id = request.data.get('product_id')
            rating = request.data.get('rating')
            comment = request.data.get('comment')

            # Проверяем наличие всех необходимых данных
            if not all([product_id, rating, comment]):
                return Response({
                    'error': 'Необходимо указать product_id, rating и comment'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Создаем отзыв
            review = Review.objects.create(
                product_id=product_id,
                user=request.user,
                rating=rating,
                comment=comment
            )

            # Возвращаем данные с именем пользователя
            return Response({
                'success': True,
                'review': {
                    'id': review.id,
                    'user': review.user.get_full_name() or review.user.username,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at,
                    'is_owner': True
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in POST review: {str(e)}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReviewDeleteView(APIView):
    @method_decorator(check_auth_tokens)
    def delete(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
            
            # Проверяем, является ли пользователь владельцем отзыва
            if not review.is_owner(request.user):
                return Response(
                    {'error': 'У вас нет прав для удаления этого отзыва'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Review.DoesNotExist:
            return Response(
                {'error': 'Отзыв не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            
