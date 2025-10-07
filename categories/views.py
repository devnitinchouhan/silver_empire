from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from .models import Category
from .serializers import CategorySerializer, CategoryListSerializer, CategoryTreeSerializer


class CategoryListView(generics.ListAPIView):
    """
    List all active categories with optional filtering and search
    """
    serializer_class = CategoryListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Category.active_objects.all()
        
        # Filter by parent category
        parent_id = self.request.query_params.get('parent')
        if parent_id is not None:
            if parent_id == '0' or parent_id.lower() == 'null':
                # Get root categories (no parent)
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        
        # Search by name or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Filter by level
        level = self.request.query_params.get('level')
        if level is not None:
            # This would require a custom filter since level is a property
            # For now, we'll skip this complex filtering
            pass
        
        return queryset.order_by('sort_order', 'name')


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific category with its subcategories
    """
    queryset = Category.active_objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


@api_view(['GET'])
@permission_classes([AllowAny])
def category_tree(request):
    """
    Get complete category tree (hierarchical structure)
    """
    # Get only root categories (no parent)
    root_categories = Category.active_objects.filter(parent__isnull=True).order_by('sort_order', 'name')
    serializer = CategoryTreeSerializer(root_categories, many=True)
    
    return Response({
        'message': 'Category tree retrieved successfully',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def category_breadcrumb(request, pk):
    """
    Get breadcrumb path for a specific category
    """
    try:
        category = Category.active_objects.get(pk=pk)
        ancestors = list(category.get_ancestors())
        ancestors.append(category)
        
        breadcrumb = [
            {
                'id': cat.id,
                'name': cat.name,
                'level': cat.level
            }
            for cat in ancestors
        ]
        
        return Response({
            'message': 'Category breadcrumb retrieved successfully',
            'data': breadcrumb
        }, status=status.HTTP_200_OK)
        
    except Category.DoesNotExist:
        return Response({
            'error': 'Category not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def root_categories(request):
    """
    Get only root categories (categories with no parent)
    """
    categories = Category.active_objects.filter(parent__isnull=True).order_by('sort_order', 'name')
    serializer = CategoryListSerializer(categories, many=True)
    
    return Response({
        'message': 'Root categories retrieved successfully',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def category_children(request, pk):
    """
    Get direct children of a specific category
    """
    try:
        category = Category.active_objects.get(pk=pk)
        children = category.subcategories.filter(is_active=True).order_by('sort_order', 'name')
        serializer = CategoryListSerializer(children, many=True)
        
        return Response({
            'message': f'Children of category "{category.name}" retrieved successfully',
            'parent': {
                'id': category.id,
                'name': category.name,
                'full_path': category.full_path
            },
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Category.DoesNotExist:
        return Response({
            'error': 'Category not found'
        }, status=status.HTTP_404_NOT_FOUND)
