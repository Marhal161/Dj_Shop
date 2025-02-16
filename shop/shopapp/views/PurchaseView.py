from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from ..models import Product, Purchase, BalanceTransaction
from ..decorators import check_auth_tokens
from django.utils.decorators import method_decorator

class PurchaseView(APIView):
    @method_decorator(check_auth_tokens)
    def post(self, request, game_id):
        try:
            with transaction.atomic():
                # Получаем игру
                game = Product.objects.select_for_update().get(id=game_id)
                user = request.user

                # Проверяем наличие
                if game.available_quantity < 1:
                    BalanceTransaction.objects.create(
                        user=user,
                        amount=game.price,
                        transaction_type='PURCHASE_FAILED',
                        description=f'Нет в наличии: {game.name}'
                    )
                    return Response({
                        'error': 'Игра не доступна для покупки',
                        'redirect': False
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Проверяем баланс
                if user.balance < game.price:
                    BalanceTransaction.objects.create(
                        user=user,
                        amount=game.price,
                        transaction_type='PURCHASE_FAILED',
                        description=f'Недостаточно средств для покупки {game.name}'
                    )
                    return Response({
                        'error': 'Недостаточно средств',
                        'redirect': True,
                        'redirect_url': '/shopapp/profile/'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Создаем покупку
                purchase = Purchase.objects.create(
                    user=user,
                    game=game,
                    price=game.price
                )

                # Обновляем количество игр и баланс пользователя
                game.available_quantity -= 1
                game.save()

                user.balance -= game.price
                user.save()

                # Создаем запись об успешной покупке с ключом
                BalanceTransaction.objects.create(
                    user=user,
                    amount=game.price,
                    transaction_type='PURCHASE_SUCCESS',
                    description=f'Покупка игры {game.name}',
                    game_key=purchase.game_key
                )

                return Response({
                    'message': 'Игра успешно куплена',
                    'game_key': purchase.game_key,
                    'price': str(purchase.price),
                    'new_balance': str(user.balance)
                }, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Игра не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PurchaseHistoryView(APIView):
    @method_decorator(check_auth_tokens)
    def get(self, request):
        try:
            purchases = Purchase.objects.filter(user=request.user)
            data = [{
                'game_name': purchase.game.name,
                'game_key': purchase.game_key,
                'price': str(purchase.price),
                'date': purchase.created_at.strftime('%d.%m.%Y %H:%M')
            } for purchase in purchases]
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 