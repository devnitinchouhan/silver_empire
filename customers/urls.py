from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'customers'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.CustomerProfileView.as_view(), name='profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]