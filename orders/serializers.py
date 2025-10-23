# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, ShippingMethod, OrderStatus
from products.serializers import ProductListSerializer
from accounts.serializers import AddressSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    # product field removed because OrderItem.product is not defined on the model
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        # explicitly list fields that exist on the model
        fields = ('id', 'order', 'quantity', 'price_at_purchase', 'item_total')
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
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'status_display',
                 'total_amount', 'item_count', 'created_at')

    def get_total_amount(self, obj):
        return obj.total_amount

    def get_item_count(self, obj):
        return obj.items.count()

class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # Addresses are not currently defined on Order model; keep payload minimal
    # If you add shipping_address/billing_address fields to the model, restore these.

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'status_display',
                 'items', 'shipping_method', 'total_amount',
                 'tracking_number', 'created_at', 'updated_at')

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        # Only include fields that exist on the model. Extend once addresses/notes exist.
        fields = ('shipping_method',)

    def create(self, validated_data):
        # This will be handled in the view
        return super().create(validated_data)