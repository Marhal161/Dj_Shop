from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.RegisterView import RegisterView
from .views.LoginView import LoginView
from .views.LogoutView import LogoutView
# from .views.ProjectView import ProjectView
from .views.page_views import auth_page, home_page
from .views.GameView import GameView
urlpatterns = [
    path('', GameView.as_view(), name='game_view'),  # Убедитесь, что это правильно
    # Страница авторизации
    path('auth/', auth_page, name='auth_page'),
    # API endpoints
    path('api/login/', LoginView.as_view(), name='login_api'),
    path('api/register/', RegisterView.as_view(), name='register_api'),     
    path('api/logout/', LogoutView.as_view(), name='logout'),

    #path('projects/', ProjectView.as_view(), name='projects'),
    #path('projects/create/', ProjectView.as_view(), name='projects_create'),
    #path('projects/<int:project_id>/', ProjectView.as_view(), name='project_delete'),
    
]
