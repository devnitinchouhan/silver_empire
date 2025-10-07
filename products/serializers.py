from rest_framework import serializers
from django.conf import settings
from .models import Product, ProductVariation, ProductVariationAttribute, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'sort_order']


class ProductVariationAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariationAttribute
        fields = ['id', 'attribute_name', 'attribute_value']


class ProductVariationSerializer(serializers.ModelSerializer):
    attributes = ProductVariationAttributeSerializer(many=True, read_only=True)
    current_price = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = ProductVariation
        fields = [
            'id', 'name', 'sku', 'price', 'sale_price', 'current_price',
            'is_on_sale', 'discount_percentage', 'stock_quantity', 'is_in_stock',
            'attributes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product listing"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_path = serializers.CharField(source='category.full_path', read_only=True)
    primary_image = serializers.SerializerMethodField()
    current_price = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    variation_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'short_description', 'sku', 'category', 'category_name',
            'category_path', 'primary_image', 'base_price', 'sale_price',
            'current_price', 'is_on_sale', 'discount_percentage', 'is_featured',
            'is_in_stock', 'is_low_stock', 'variation_count', 'created_at'
        ]

    def get_primary_image(self, obj):
        """Get primary image or first image with relative path"""
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = obj.images.first()
        
        if primary_image:
            return {
                'id': primary_image.id,
                'image': primary_image.image.url if primary_image.image else None,
                'alt_text': primary_image.alt_text
            }
        return None

    def get_variation_count(self, obj):
        """Get count of active variations"""
        return obj.variations.filter(is_active=True, is_deleted=False).count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_path = serializers.CharField(source='category.full_path', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    current_price = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    total_stock = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'short_description', 'sku',
            'category', 'category_name', 'category_path', 'meta_title',
            'meta_description', 'base_price', 'sale_price', 'current_price',
            'is_on_sale', 'discount_percentage', 'is_featured', 'track_inventory',
            'stock_quantity', 'total_stock', 'is_in_stock', 'is_low_stock',
            'low_stock_threshold', 'images', 'variations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSearchSerializer(serializers.ModelSerializer):
    """Minimal serializer for search results"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    current_price = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'short_description', 'sku', 'category_name',
            'primary_image', 'current_price', 'is_on_sale', 'is_featured'
        ]

    def get_primary_image(self, obj):
        """Get primary image URL only"""
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = obj.images.first()
        
        if primary_image and primary_image.image:
            return primary_image.image.url
        return None