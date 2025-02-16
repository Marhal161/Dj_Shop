from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.RegisterView import RegisterView
from .views.LoginView import LoginView
from .views.LogoutView import LogoutView
from .views.page_views import auth_page, home_page, profile_page, balance_page, cart_page
from .views.GameView import GameView, game_detail, GamesListView, games_api, categories_api
from .views.ReviewView import ReviewView, ReviewDeleteView
from .views.ProfileView import ProfileView, ProfileBalanceView, ProfileBalanceTransactionsView
from .views.PurchaseView import PurchaseView, PurchaseHistoryView
from .views.CartView import CartView, CartItemView, CartCheckoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Главная страница (защищена декоратором в GameView)
    path('', GameView.as_view(), name='game_view'),
    path('game/<int:game_id>/', game_detail, name='game_detail'),
    path('auth/', auth_page, name='auth'),
    path('profile/', profile_page, name='profile'),
    path('profile/balance/', balance_page, name='profile-balance'),
    path('cart/', cart_page, name='cart'),
    # API endpoints
    path('api/login/', LoginView.as_view(), name='login_api'),
    path('api/register/', RegisterView.as_view(), name='register_api'),     
    path('api/review/', ReviewView.as_view(), name='review'),  # Добавляем URL для отзывов
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', ProfileView.as_view(), name='profile-api'),
    path('api/profile/balance/', ProfileBalanceView.as_view(), name='profile-balance-api'),
    path('api/profile/balance/transactions/', ProfileBalanceTransactionsView.as_view(), name='profile-balance-transactions-api'),
    path('games/', GamesListView.as_view(), name='games_list'),
    path('api/games/', games_api, name='games_api'),
    path('api/categories/', categories_api, name='categories_api'),
    path('api/games/<int:game_id>/purchase/', PurchaseView.as_view(), name='purchase_game'),
    path('api/purchases/', PurchaseHistoryView.as_view(), name='purchase_history'),
    path('api/cart/', CartView.as_view(), name='cart'),
    path('api/cart/items/<int:item_id>/', CartItemView.as_view(), name='cart-item'),
    path('api/cart/checkout/', CartCheckoutView.as_view(), name='cart-checkout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/review/<int:review_id>/', ReviewDeleteView.as_view(), name='review-delete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

