# analytics/serializers.py
from rest_framework import serializers
from .models import PageView, ProductView, SalesReport

class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = '__all__'

class ProductViewSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductView
        fields = '__all__'

class SalesReportSerializer(serializers.ModelSerializer):
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_orders = serializers.IntegerField(read_only=True)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = SalesReport
        fields = '__all__'