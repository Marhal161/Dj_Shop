from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.shortcuts import redirect
from django.http import HttpResponse

class LogoutView(APIView):
    @staticmethod
    def get(request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            response = Response({
                'success': True,
                'message': 'Вы успешно вышли из системы.'
            }, status=status.HTTP_200_OK)
            
            # Удаляем токены
            response.delete_cookie('access_token', path='/')
            response.delete_cookie('refresh_token', path='/')
            
            # Добавляем заголовки для CORS, если необходимо
            response["Access-Control-Allow-Credentials"] = "true"
            
            return response

        except Exception as e:
            return Response({
                'success': False,
                'message': f'Ошибка при выходе из системы: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        response = HttpResponse()
        # Удаляем токены из куки
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
