# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, ShippingMethod, OrderStatus
from products.serializers import ProductListSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'variant', 'quantity', 'price_at_purchase', 'item_total')
        read_only_fields = ('order', 'item_total')

    def get_item_total(self, obj):
        return obj.quantity * obj.price_at_purchase

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = '__all__'

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'

class OrderListSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='status.name', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'status_name',
                 'total_amount', 'item_count', 'created_at')

    def get_item_count(self, obj):
        return obj.items.count()

class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'status_name',
                 'items', 'shipping_method', 'total_amount',
                 'tracking_number', 'created_at', 'updated_at')

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('shipping_method', 'total_amount')

    def create(self, validated_data):
        return Order.objects.create(**validated_data)