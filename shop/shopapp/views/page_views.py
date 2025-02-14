from django.shortcuts import render

def auth_page(request):
    return render(request, 'auth.html')

def home_page(request):
    return render(request, 'main.html')