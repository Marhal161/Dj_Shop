from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers.LoginSerializer import LogSerializer


class LoginView(APIView):
    @staticmethod
    def post(request):
        serializer = LogSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Создание токенов JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Установка куки
            response = Response({
                'success': True,
                'access_token': access_token,
                'refresh_token': str(refresh),
                'user_id': user.id  # Отправляем только ID пользователя
            }, status=status.HTTP_200_OK)
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', str(refresh), httponly=True)

            return response
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
