from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

class LogoutView(APIView):
    @staticmethod
    def get(request):
        try:
            refresh_token_str = request.COOKIES.get('refresh_token')

            if refresh_token_str:
                # Обновляем RefreshToken
                refresh_token = RefreshToken(refresh_token_str)
                refresh_token.set_jti()  # Устанавливаем новый jti

                # Удаляем токен из куки
                response = Response({
                    'success': True,
                    'message': 'Вы успешно вышли из системы.'
                }, status=status.HTTP_200_OK)
                response.delete_cookie('access_token')  # Удаляем access_token
                response.delete_cookie('refresh_token')  # Удаляем refresh_token
                return response

            else:
                return Response({
                    'success': False,
                    'message': 'Нет активного сеанса.'
                }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({
                'success': False,
                'message': f'Ошибка при выходе из системы: {e}'
            }, status=status.HTTP_400_BAD_REQUEST)
