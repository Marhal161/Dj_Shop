from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from ..serializers import RegisterSerializer
from ..models import User

class RegisterView(APIView):
    @staticmethod
    def post(request):
        try:
            # Валидация пароля
            validate_password(request.data.get('password'))
            
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    user = serializer.save()

                    # Создание токенов JWT
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)

                    response_data = {
                        'success': True,
                        'message': 'Регистрация успешна!',
                        'user': {
                            'id': user.id,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'email': user.email,
                            'username': user.username,
                        }
                    }

                    # Создаем ответ
                    response = JsonResponse(response_data, status=status.HTTP_201_CREATED)
                    
                    # Устанавливаем куки
                    response.set_cookie('access_token', access_token, httponly=True)
                    response.set_cookie('refresh_token', str(refresh), httponly=True)

                    return response

                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': 'Ошибка при создании пользователя',
                        'errors': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Возвращаем ошибки валидации сериализатора
            return JsonResponse({
                'success': False,
                'message': 'Ошибка в введенных данных',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            # Ошибки валидации пароля
            return JsonResponse({
                'success': False,
                'message': 'Ошибка валидации пароля',
                'errors': list(e.messages)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Общие ошибки
            return JsonResponse({
                'success': False,
                'message': 'Произошла неизвестная ошибка',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)