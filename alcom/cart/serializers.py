# cart/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem, Coupon, Discount
from products.models import Product
from products.serializers import ProductListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'product', 'product_id', 'quantity', 'total_price')
        read_only_fields = ('cart', 'total_price')

    def get_total_price(self, obj):
        return obj.quantity * obj.product.price

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_items', 'total_price', 
                 'coupon', 'discount_amount', 'final_price', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')

    def get_total_items(self, obj):
        return obj.items.count()

    def get_total_price(self, obj):
        return sum(item.quantity * item.product.price for item in obj.items.all())

    def get_discount_amount(self, obj):
        if obj.coupon:
            total = self.get_total_price(obj)
            return obj.coupon.calculate_discount(total)
        return 0

    def get_final_price(self, obj):
        total = self.get_total_price(obj)
        discount = self.get_discount_amount(obj)
        return max(0, total - discount)

class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = '__all__'

    def get_is_valid(self, obj):
        return obj.is_valid()

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'