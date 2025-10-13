from rest_framework import serializers
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from .models import Order, OrderItem


from products.models import Product, ProductVariation


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'variation', 'quantity', 'unit_price']
        # unit_price is computed server-side
        read_only_fields = ['id', 'product_name', 'unit_price']

    def validate(self, attrs):
        # Ensure product exists and variation (if provided) belongs to product
        product = attrs.get('product')
        variation = attrs.get('variation')
        if variation and product and variation.product_id != product.id:
            raise serializers.ValidationError('Variation does not belong to the given product')
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField(read_only=True)
    items = OrderItemSerializer(many=True)

    shipping_address = serializers.CharField(required=False, allow_blank=True)
    shipping_city = serializers.CharField(required=False, allow_blank=True)
    shipping_postal_code = serializers.CharField(required=False, allow_blank=True)
    shipping_country = serializers.CharField(required=False, allow_blank=True)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer', 'total_amount', 'status', 'items',
            'shipping_address', 'shipping_city', 'shipping_postal_code',
            'shipping_country', 'shipping_cost', 'created_at'
        ]
        # customer, total_amount are computed/derived — read-only
        read_only_fields = ['id', 'order_id', 'created_at', 'customer', 'total_amount']

    def get_order_id(self, obj):
        return obj.order_id

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['customer'] = request.user

        items_data = validated_data.pop('items', [])

        # shipping cost default
        shipping_cost = validated_data.get('shipping_cost') or Decimal('0.00')

        with transaction.atomic():
            # remove any customer from validated_data (we set from request)
            if 'customer' in validated_data:
                validated_data.pop('customer')

            order = Order.objects.create(**validated_data)

            total = Decimal('0.00')
            for item in items_data:
                product = item.get('product')
                variation = item.get('variation')
                quantity = int(item.get('quantity', 1))

                # Determine unit price: variation current_price if present, otherwise product current_price/base_price
                unit_price = None
                if variation:
                    unit_price = getattr(variation, 'current_price', None)
                elif product:
                    unit_price = getattr(product, 'current_price', None) or getattr(product, 'base_price', None)

                if unit_price is None:
                    unit_price = Decimal(str(item.get('unit_price', '0.00')))
                else:
                    unit_price = Decimal(str(unit_price))

                # Round to 2 decimal places
                unit_price = unit_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variation=variation,
                    quantity=quantity,
                    unit_price=unit_price
                )

                total += (unit_price * Decimal(quantity))

            # add shipping cost (ensure Decimal)
            shipping_cost = Decimal(str(shipping_cost))
            shipping_cost = shipping_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total += shipping_cost

            order.total_amount = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            order.shipping_cost = shipping_cost
            order.save()

        return order
