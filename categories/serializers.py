from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    level = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()
    is_leaf = serializers.ReadOnlyField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'parent', 'parent_name',
            'is_active', 'sort_order', 'level', 'full_path', 'is_leaf',
            'subcategories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image(self, obj):
        """Return relative path for image"""
        if obj.image:
            return obj.image.url
        return None

    def get_subcategories(self, obj):
        """Get immediate subcategories only"""
        subcategories = obj.subcategories.filter(is_active=True).order_by('sort_order', 'name')
        return CategoryListSerializer(subcategories, many=True).data


class CategoryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing categories without nested subcategories"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    level = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()
    subcategory_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'parent', 'parent_name',
            'is_active', 'sort_order', 'level', 'full_path', 'subcategory_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image(self, obj):
        """Return relative path for image"""
        if obj.image:
            return obj.image.url
        return None

    def get_subcategory_count(self, obj):
        """Get count of active subcategories"""
        return obj.subcategories.filter(is_active=True).count()


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer for hierarchical tree view of categories"""
    children = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'sort_order', 'children']

    def get_image(self, obj):
        """Return relative path for image"""
        if obj.image:
            return obj.image.url
        return None