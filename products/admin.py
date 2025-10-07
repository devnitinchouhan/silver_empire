from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductVariation, ProductVariationAttribute, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']


class ProductVariationAttributeInline(admin.TabularInline):
    model = ProductVariationAttribute
    extra = 1
    fields = ['attribute_name', 'attribute_value']


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 0
    fields = ['name', 'sku', 'price', 'sale_price', 'stock_quantity', 'is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'current_price', 'stock_indicator',
        'is_featured', 'is_active', 'is_deleted', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_featured', 'is_deleted', 'category', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description']
    list_editable = ['is_featured', 'is_active']
    ordering = ['-created_at']
    inlines = [ProductImageInline, ProductVariationInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'short_description', 'sku', 'category')
        }),
        ('Pricing', {
            'fields': ('base_price', 'sale_price')
        }),
        ('Inventory', {
            'fields': ('track_inventory', 'stock_quantity', 'low_stock_threshold')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_deleted')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'deleted_by', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    
    def stock_indicator(self, obj):
        """Visual indicator for stock status"""
        if not obj.track_inventory:
            return format_html('<span style="color: blue;">∞ (Not tracked)</span>')
        
        total_stock = obj.total_stock
        if total_stock == 0:
            return format_html('<span style="color: red;">⚠ Out of stock</span>')
        elif total_stock <= obj.low_stock_threshold:
            return format_html('<span style="color: orange;">⚠ Low stock ({})</span>', total_stock)
        else:
            return format_html('<span style="color: green;">✓ In stock ({})</span>', total_stock)
    
    stock_indicator.short_description = 'Stock Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['activate_products', 'deactivate_products', 'mark_featured', 'unmark_featured', 'soft_delete_products']
    
    def activate_products(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} products were activated.')
    activate_products.short_description = "Activate selected products"
    
    def deactivate_products(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} products were deactivated.')
    deactivate_products.short_description = "Deactivate selected products"
    
    def mark_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} products were marked as featured.')
    mark_featured.short_description = "Mark as featured"
    
    def unmark_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} products were unmarked as featured.')
    unmark_featured.short_description = "Unmark as featured"
    
    def soft_delete_products(self, request, queryset):
        count = 0
        for product in queryset:
            if not product.is_deleted:
                product.soft_delete(deleted_by=request.user)
                count += 1
        self.message_user(request, f'{count} products were soft deleted.')
    soft_delete_products.short_description = "Soft delete selected products"


@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'product', 'sku', 'current_price', 'stock_quantity',
        'is_active', 'is_deleted', 'created_at'
    ]
    list_filter = ['is_active', 'is_deleted', 'product', 'created_at']
    search_fields = ['name', 'sku', 'product__name']
    list_editable = ['is_active']
    ordering = ['-created_at']
    inlines = [ProductVariationAttributeInline]
    
    fieldsets = (
        (None, {
            'fields': ('product', 'name', 'sku')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'deleted_by', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_tag', 'alt_text', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_primary', 'sort_order']
    ordering = ['product', 'sort_order']
    
    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    image_tag.short_description = 'Image'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
