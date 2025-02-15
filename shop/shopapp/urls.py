from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.RegisterView import RegisterView
from .views.LoginView import LoginView
from .views.LogoutView import LogoutView
from .views.page_views import auth_page, home_page, profile_page, balance_page
from .views.GameView import GameView, game_detail
from .views.ReviewView import ReviewView
from .views.ProfileView import ProfileView, ProfileBalanceView, ProfileBalanceTransactionsView

urlpatterns = [
    # Главная страница (защищена декоратором в GameView)
    path('', GameView.as_view(), name='game_view'),
    path('game/<int:pk>/', game_detail, name='game_detail'),
    path('auth/', auth_page, name='auth'),
    path('profile/', profile_page, name='profile'),
    path('profile/balance/', balance_page, name='profile-balance'),
    # API endpoints
    path('api/login/', LoginView.as_view(), name='login_api'),
    path('api/register/', RegisterView.as_view(), name='register_api'),     
    path('api/review/', ReviewView.as_view(), name='review'),  # Добавляем URL для отзывов
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', ProfileView.as_view(), name='profile-api'),
    path('api/profile/balance/', ProfileBalanceView.as_view(), name='profile-balance-api'),
    path('api/profile/balance/transactions/', ProfileBalanceTransactionsView.as_view(), name='profile-balance-transactions-api'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

