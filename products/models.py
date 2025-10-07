from django.db import models
from django.conf import settings
from django.utils import timezone


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    short_description = models.CharField(max_length=500, blank=True, null=True)
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.CharField(max_length=500, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    
    # Pricing (base prices, variations may override)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Inventory
    track_inventory = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_products'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_products'
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_products'
    )

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def soft_delete(self, deleted_by=None):
        """Soft delete the product"""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.save()
        
        # Also soft delete all variations
        for variation in self.variations.all():
            variation.soft_delete(deleted_by)

    def restore(self):
        """Restore soft deleted product"""
        self.is_deleted = False
        self.is_active = True
        self.deleted_at = None
        self.deleted_by = None
        self.save()

    @property
    def current_price(self):
        """Get current selling price (sale price if available, otherwise base price)"""
        return self.sale_price if self.sale_price else self.base_price

    @property
    def is_on_sale(self):
        """Check if product is on sale"""
        return self.sale_price is not None and self.sale_price < self.base_price

    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_on_sale:
            return round(((self.base_price - self.sale_price) / self.base_price) * 100, 2)
        return 0

    @property
    def total_stock(self):
        """Get total stock including variations"""
        if self.track_inventory:
            variation_stock = sum(
                var.stock_quantity for var in self.variations.filter(is_active=True, is_deleted=False)
            )
            return self.stock_quantity + variation_stock
        return None

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.total_stock > 0

    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        if not self.track_inventory:
            return False
        return self.total_stock <= self.low_stock_threshold


class ProductVariation(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variations'
    )
    name = models.CharField(max_length=100)  # e.g., "Silver Ring - Size 7"
    sku = models.CharField(max_length=100, unique=True)
    
    # Variation attributes (flexible key-value pairs)
    # For jewelry: size, metal_type, stone_type, etc.
    
    # Pricing (overrides product base price)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_variations'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_variations'
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_variations'
    )

    class Meta:
        db_table = 'product_variations'
        verbose_name = 'Product Variation'
        verbose_name_plural = 'Product Variations'
        ordering = ['name']

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    def soft_delete(self, deleted_by=None):
        """Soft delete the variation"""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.save()

    def restore(self):
        """Restore soft deleted variation"""
        self.is_deleted = False
        self.is_active = True
        self.deleted_at = None
        self.deleted_by = None
        self.save()

    @property
    def current_price(self):
        """Get current selling price"""
        return self.sale_price if self.sale_price else self.price

    @property
    def is_on_sale(self):
        """Check if variation is on sale"""
        return self.sale_price is not None and self.sale_price < self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_on_sale:
            return round(((self.price - self.sale_price) / self.price) * 100, 2)
        return 0

    @property
    def is_in_stock(self):
        """Check if variation is in stock"""
        return self.stock_quantity > 0


class ProductVariationAttribute(models.Model):
    """
    Flexible attributes for product variations
    e.g., size=7, metal_type=silver, stone_type=diamond
    """
    variation = models.ForeignKey(
        ProductVariation,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    attribute_name = models.CharField(max_length=50)  # size, color, metal_type, etc.
    attribute_value = models.CharField(max_length=100)  # 7, red, silver, etc.
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_variation_attributes'
        verbose_name = 'Product Variation Attribute'
        verbose_name_plural = 'Product Variation Attributes'
        unique_together = ['variation', 'attribute_name']

    def __str__(self):
        return f"{self.attribute_name}: {self.attribute_value}"


class ProductImage(models.Model):
    """Product images"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"


# Custom managers for excluding soft deleted items
class ActiveProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)


class ActiveVariationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)


# Add the active managers to models
Product.add_to_class('active_objects', ActiveProductManager())
ProductVariation.add_to_class('active_objects', ActiveVariationManager())
