"""
URL configuration for silver_empire project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint with available endpoints"""
    return Response({
        'message': 'Welcome to Silver Jewellery API',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
                'profile': '/api/auth/profile/',
                'token_refresh': '/api/auth/token/refresh/',
            },
            'categories': {
                'list': '/api/categories/',
                'detail': '/api/categories/{id}/',
                'tree': '/api/categories/tree/',
                'roots': '/api/categories/roots/',
                'children': '/api/categories/{id}/children/',
                'breadcrumb': '/api/categories/{id}/breadcrumb/',
            },
            'products': {
                'list': '/api/products/',
                'detail': '/api/products/{id}/',
                'featured': '/api/products/featured/',
                'search': '/api/products/search/',
                'stats': '/api/products/stats/',
                'variations': '/api/products/{id}/variations/',
                'related': '/api/products/{id}/related/',
                'variation_detail': '/api/products/variations/{id}/',
            }
        }
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api_root"),
    path("api/auth/", include("customers.urls")),
    path("api/categories/", include("categories.urls")),
    path("api/products/", include("products.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
