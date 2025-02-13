from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import RegisterSerializer  # Импорт сериализатора
from django.http import HttpResponse
from ..models import User


class RegisterView(APIView):
    @staticmethod
    def post(request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()

                # Создание токенов JWT
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # Установка куки
                response = HttpResponse({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'username': user.username,
                    }
                }, status=status.HTTP_201_CREATED)
                response.set_cookie('access_token', access_token, httponly=True)
                response.set_cookie('refresh_token', str(refresh), httponly=True)

                # Возвращение ответа
                return response
            except Exception as e:  # Обработка исключений
                return Response({
                    'success': False,
                    'message': 'Ошибка при создании пользователя: {}'.format(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
