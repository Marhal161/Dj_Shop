from django.shortcuts import render, redirect
from ..decorators import check_auth_tokens
from django.utils.decorators import method_decorator

def auth_page(request):
    # Страница авторизации не должна требовать авторизации
    return render(request, 'auth.html')

@check_auth_tokens  # Применяем декоратор только к защищенным страницам
def home_page(request):
    return render(request, 'main.html')

@check_auth_tokens
def profile_page(request):
    if not request.user.is_authenticated:
        return redirect('auth')
    return render(request, 'profile.html', {'user': request.user})

@check_auth_tokens
def balance_page(request):
    """
    Отображение страницы пополнения баланса.
    Доступно только авторизованным пользователям.
    """
    return render(request, 'profile.html', {
        'user': request.user,
        'page_title': 'Пополнение баланса',
        'show_balance_form': True
    })

def cart_page(request):
    return render(request, 'cart.html', {
        'is_authenticated': request.user.is_authenticated
    })
    