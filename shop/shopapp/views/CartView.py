from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from ..models import Cart, CartItem, Product, Purchase, BalanceTransaction
from ..decorators import check_auth_tokens
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

@method_decorator(csrf_exempt, name='dispatch')
class CartView(APIView):
    @method_decorator(check_auth_tokens)
    def get(self, request):
        """Получение содержимого корзины"""
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            items = cart.cartitem_set.all()
            total_items = sum(item.quantity for item in items)  # Добавляем подсчет общего количества
            
            data = {
                'items': [{
                    'id': item.id,
                    'product_id': item.product.id,
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'quantity': item.quantity,
                    'total_price': str(item.get_total_price())
                } for item in items],
                'total': str(cart.get_total_price()),
                'total_items': total_items  # Добавляем в ответ
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @method_decorator(check_auth_tokens)
    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity', 1)

            if not product_id:
                return Response({'error': 'Не указан ID продукта'}, status=status.HTTP_400_BAD_REQUEST)

            # Получаем продукт
            product = get_object_or_404(Product, id=product_id)

            # Проверяем наличие
            if product.available_quantity < quantity:
                return Response(
                    {'error': 'Недостаточно товара на складе'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Получаем или создаем корзину для пользователя
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Получаем или создаем элемент корзины
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            # Если элемент уже существовал, увеличиваем количество
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response({
                'message': 'Товар добавлен в корзину',
                'cart_total': cart.get_total_price()
            })

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CartItemView(APIView):
    @method_decorator(check_auth_tokens)
    def delete(self, request, item_id):
        """Удаление товара из корзины"""
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Товар не найден в корзине'},
                status=status.HTTP_404_NOT_FOUND
            )

class CartCheckoutView(APIView):
    @method_decorator(check_auth_tokens)
    def post(self, request):
        """Оформление покупки из корзины"""
        try:
            with transaction.atomic():
                cart = Cart.objects.get(user=request.user)
                total_price = cart.get_total_price()
                
                # Проверяем баланс
                if request.user.balance < total_price:
                    BalanceTransaction.objects.create(
                        user=request.user,
                        amount=total_price,
                        transaction_type='PURCHASE_FAILED',
                        description='Недостаточно средств для покупки игр из корзины'
                    )
                    return Response({
                        'error': 'Недостаточно средств',
                        'redirect': True,
                        'redirect_url': '/shopapp/profile/'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Проверяем наличие всех игр
                for item in cart.cartitem_set.all():
                    if item.product.available_quantity < item.quantity:
                        return Response({
                            'error': f'Игра {item.product.name} недоступна в нужном количестве'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Создаем покупки и обновляем количество
                purchases = []
                for item in cart.cartitem_set.all():
                    # Создаем нужное количество покупок
                    for _ in range(item.quantity):
                        purchase = Purchase.objects.create(
                            user=request.user,
                            game=item.product,
                            price=item.product.price
                        )
                        purchases.append(purchase)
                    
                    # Обновляем количество
                    item.product.available_quantity -= item.quantity
                    item.product.save()
                    
                    # Создаем запись о покупке
                    BalanceTransaction.objects.create(
                        user=request.user,
                        amount=item.get_total_price(),
                        transaction_type='PURCHASE_SUCCESS',
                        description=f'Покупка игры {item.product.name} ({item.quantity} шт.)',
                        game_key=', '.join(p.game_key for p in purchases[-item.quantity:])  # Добавляем все ключи
                    )
                
                # Списываем деньги
                request.user.balance -= total_price
                request.user.save()
                
                # Очищаем корзину
                cart.cartitem_set.all().delete()
                
                return Response({
                    'message': 'Покупка успешно оформлена',
                    'purchases': [{
                        'game_name': p.game.name,
                        'game_key': p.game_key,
                        'price': str(p.price)
                    } for p in purchases],
                    'total_price': str(total_price),
                    'new_balance': str(request.user.balance)
                }, status=status.HTTP_200_OK)
                
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Корзина не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 