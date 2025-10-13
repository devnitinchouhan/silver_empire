from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListCreateView.as_view(), name='order_list_create'),
    path('<int:id>/', views.OrderDetailView.as_view(), name='order_detail'),
]
