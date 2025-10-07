from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q, Min, Max
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from .models import Product, ProductVariation
from .serializers import (
    ProductListSerializer, 
    ProductDetailSerializer, 
    ProductSearchSerializer,
    ProductVariationSerializer
)
from .pagination import ProductPagination, StandardPagination


class ProductFilter(django_filters.FilterSet):
    """Custom filter for products with enhanced options"""
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = django_filters.NumberFilter(field_name='category__id')
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_price = django_filters.NumberFilter(method='filter_max_price')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    sort_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('base_price', 'price'),
            ('created_at', 'newest'),
            ('-created_at', 'oldest'),
            ('base_price', 'price_low_to_high'),
            ('-base_price', 'price_high_to_low'),
        ),
        field_labels={
            'name': 'Name A-Z',
            '-name': 'Name Z-A',
            'price': 'Price Low to High',
            '-price': 'Price High to Low',
            'newest': 'Newest First',
            'oldest': 'Oldest First',
        }
    )
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'min_price', 'max_price', 'in_stock', 'is_featured']
    
    def filter_min_price(self, queryset, name, value):
        """Filter products by minimum price (considering sale price)"""
        return queryset.filter(
            Q(sale_price__gte=value) | 
            (Q(sale_price__isnull=True) & Q(base_price__gte=value))
        )
    
    def filter_max_price(self, queryset, name, value):
        """Filter products by maximum price (considering sale price)"""
        return queryset.filter(
            Q(sale_price__lte=value) | 
            (Q(sale_price__isnull=True) & Q(base_price__lte=value))
        )
    
    def filter_in_stock(self, queryset, name, value):
        """Filter products by stock availability"""
        if value:
            return queryset.filter(
                Q(track_inventory=False) | Q(stock_quantity__gt=0)
            )
        return queryset


class ProductListView(generics.ListAPIView):
    """
    List all active products with enhanced filtering, search, and ordering
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['name', 'base_price', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.active_objects.select_related('category').prefetch_related('images')
        
        # Additional category filtering with descendants support
        category_id = self.request.query_params.get('category')
        if category_id:
            try:
                from categories.models import Category
                category = Category.objects.get(id=category_id)
                # Get category and all its descendants
                descendant_ids = [desc.id for desc in category.get_descendants()]
                category_ids = [category.id] + descendant_ids
                queryset = queryset.filter(category_id__in=category_ids)
            except Category.DoesNotExist:
                pass
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list method to provide additional metadata"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get filter statistics
        stats = {
            'total_products': queryset.count(),
            'price_range': queryset.aggregate(
                min_price=Min('base_price'),
                max_price=Max('base_price')
            ),
            'available_categories': list(
                queryset.values_list('category__name', flat=True).distinct()
            )
        }
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['stats'] = stats
            response.data['filters'] = {
                'category': request.query_params.get('category'),
                'min_price': request.query_params.get('min_price'),
                'max_price': request.query_params.get('max_price'),
                'in_stock': request.query_params.get('in_stock'),
                'is_featured': request.query_params.get('is_featured'),
                'search': request.query_params.get('search'),
                'ordering': request.query_params.get('ordering'),
            }
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'stats': stats
        })


class ProductDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific product with full details
    """
    queryset = Product.active_objects.select_related('category').prefetch_related(
        'images', 'variations__attributes'
    )
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]


class FeaturedProductsView(generics.ListAPIView):
    """
    Get featured products with pagination
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return Product.active_objects.filter(
            is_featured=True
        ).select_related('category').prefetch_related('images')


class ProductSearchView(generics.ListAPIView):
    """
    Advanced product search with pagination
    """
    serializer_class = ProductSearchSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()
        if not query:
            return Product.objects.none()
        
        return Product.active_objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(sku__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('category').prefetch_related('images').distinct()


@api_view(['GET'])
@permission_classes([AllowAny])
def product_variations(request, pk):
    """
    Get all variations for a specific product
    """
    try:
        product = Product.active_objects.get(pk=pk)
        variations = product.variations.filter(is_active=True, is_deleted=False)
        serializer = ProductVariationSerializer(variations, many=True)
        
        return Response({
            'message': f'Variations for product "{product.name}" retrieved successfully',
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku
            },
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_stats(request):
    """
    Get product statistics
    """
    stats = {
        'total_products': Product.active_objects.count(),
        'featured_products': Product.active_objects.filter(is_featured=True).count(),
        'categories_with_products': Product.active_objects.values('category__name').distinct().count(),
        'price_range': Product.active_objects.aggregate(
            min_price=Min('base_price'),
            max_price=Max('base_price')
        ),
        'in_stock_products': Product.active_objects.filter(
            Q(track_inventory=False) | Q(stock_quantity__gt=0)
        ).count(),
        'out_of_stock_products': Product.active_objects.filter(
            track_inventory=True,
            stock_quantity=0
        ).count(),
    }
    
    return Response({
        'message': 'Product statistics retrieved successfully',
        'data': stats
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def variation_detail(request, pk):
    """
    Get details of a specific product variation
    """
    try:
        variation = ProductVariation.active_objects.select_related(
            'product'
        ).prefetch_related('attributes').get(pk=pk)
        
        serializer = ProductVariationSerializer(variation)
        
        return Response({
            'message': 'Variation details retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except ProductVariation.DoesNotExist:
        return Response({
            'error': 'Product variation not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_stats(request):
    """
    Get product statistics
    """
    total_products = Product.active_objects.count()
    featured_products = Product.active_objects.filter(is_featured=True).count()
    in_stock_products = Product.active_objects.filter(
        Q(track_inventory=False) | Q(stock_quantity__gt=0)
    ).count()
    
    # Price range
    price_stats = Product.active_objects.aggregate(
        min_price=Min('base_price'),
        max_price=Max('base_price')
    )
    
    return Response({
        'message': 'Product statistics retrieved successfully',
        'data': {
            'total_products': total_products,
            'featured_products': featured_products,
            'in_stock_products': in_stock_products,
            'out_of_stock_products': total_products - in_stock_products,
            'price_range': {
                'min_price': price_stats['min_price'] or 0,
                'max_price': price_stats['max_price'] or 0
            }
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def related_products(request, pk):
    """
    Get related products based on category
    """
    try:
        product = Product.active_objects.get(pk=pk)
        
        # Get products from the same category, excluding the current product
        related = Product.active_objects.filter(
            category=product.category
        ).exclude(id=product.id).select_related('category').prefetch_related('images')[:6]
        
        serializer = ProductListSerializer(related, many=True)
        
        return Response({
            'message': 'Related products retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
