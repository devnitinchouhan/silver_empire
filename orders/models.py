from django.db import models
from django.conf import settings
from django.utils import timezone


class Order(models.Model):
    """
    Basic Order model. Primary key remains numeric (id).
    Expose a read-only `order_id` property which is "ORD" + id.
    """
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, default='pending')
    # Shipping details
    shipping_address = models.CharField(max_length=500, blank=True, null=True)
    shipping_city = models.CharField(max_length=200, blank=True, null=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True, null=True)
    shipping_country = models.CharField(max_length=100, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Audit / soft delete
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"{self.order_id} - {self.customer}"

    @property
    def order_id(self):
        """Return the prefixed order id, e.g. ORD123"""
        return f"ORD{self.id}" if self.id is not None else None

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    variation = models.ForeignKey('products.ProductVariation', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.order.order_id} - Item {self.id}"


# Active manager to exclude soft deleted orders
class ActiveOrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


Order.add_to_class('active_objects', ActiveOrderManager())
