from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('featured/', views.FeaturedProductsView.as_view(), name='featured_products'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('stats/', views.product_stats, name='product_stats'),
    path('<int:pk>/variations/', views.product_variations, name='product_variations'),
    path('<int:pk>/related/', views.related_products, name='related_products'),
    path('variations/<int:pk>/', views.variation_detail, name='variation_detail'),
]