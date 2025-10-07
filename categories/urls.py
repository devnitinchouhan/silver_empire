from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tree/', views.category_tree, name='category_tree'),
    path('roots/', views.root_categories, name='root_categories'),
    path('<int:pk>/children/', views.category_children, name='category_children'),
    path('<int:pk>/breadcrumb/', views.category_breadcrumb, name='category_breadcrumb'),
]