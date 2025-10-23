# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, ShippingMethod, OrderStatus
from products.serializers import ProductListSerializer
from accounts.serializers import AddressSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ('order', 'item_total')

    def get_item_total(self, obj):
        return obj.quantity * obj.price

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = '__all__'

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'

class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'user', 'status', 'status_display',
                 'total_amount', 'item_count', 'created_at')

    def get_total_amount(self, obj):
        return obj.total_amount

    def get_item_count(self, obj):
        return obj.items.count()

class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'user', 'status', 'status_display',
                 'items', 'shipping_address', 'billing_address',
                 'shipping_method', 'shipping_cost', 'tax_amount',
                 'discount_amount', 'total_amount', 'payment_status',
                 'notes', 'created_at', 'updated_at')

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('shipping_address', 'billing_address', 'shipping_method', 'notes')

    def create(self, validated_data):
        # This will be handled in the view
        return super().create(validated_data)