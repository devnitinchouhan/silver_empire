from rest_framework import serializers
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from .models import Order, OrderItem


from products.models import Product, ProductVariation


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    product_variation_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'variation', 'quantity', 'unit_price', 'product_id', 'product_variation_id']
        read_only_fields = ['id', 'product', 'product_name', 'variation', 'unit_price']

    def validate(self, attrs):
        product_id = attrs.get('product_id')
        product_variation_id = attrs.get('product_variation_id')

        if not product_id and not product_variation_id:
            raise serializers.ValidationError("Either 'product_id' or 'product_variation_id' is required.")

        if product_variation_id:
            try:
                variation = ProductVariation.objects.select_related('product').get(pk=product_variation_id)
                attrs['variation'] = variation
                attrs['product'] = variation.product
            except ProductVariation.DoesNotExist:
                raise serializers.ValidationError({'product_variation_id': 'Invalid product variation.'})
        elif product_id:
            try:
                product = Product.objects.get(pk=product_id)
                attrs['product'] = product
                attrs['variation'] = None
            except Product.DoesNotExist:
                raise serializers.ValidationError({'product_id': 'Invalid product.'})

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField(read_only=True)
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer', 'total_amount', 'status', 'items',
            'shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip_code',
            'shipping_country', 'shipping_cost', 'created_at'
        ]
        read_only_fields = ['id', 'order_id', 'created_at', 'customer', 'total_amount']

    def get_order_id(self, obj):
        return obj.order_id

    def create(self, validated_data):
        request = self.context.get('request')
        customer = request.user if request and hasattr(request, 'user') else None

        items_data = validated_data.pop('items', [])
        shipping_cost = validated_data.get('shipping_cost', Decimal('0.00'))

        with transaction.atomic():
            order = Order.objects.create(customer=customer, **validated_data)

            total = Decimal('0.00')
            for item_data in items_data:
                product = item_data.get('product')
                variation = item_data.get('variation')
                quantity = item_data.get('quantity', 1)

                unit_price = Decimal('0.00')
                if variation and variation.current_price is not None:
                    unit_price = variation.current_price
                elif product and product.current_price is not None:
                    unit_price = product.current_price
                elif product and product.base_price is not None:
                    unit_price = product.base_price

                unit_price = unit_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variation=variation,
                    quantity=quantity,
                    unit_price=unit_price
                )
                total += (unit_price * Decimal(quantity))

            order.total_amount = total + shipping_cost
            order.save()

        return order
