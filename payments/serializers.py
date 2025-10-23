
# payments/serializers.py
from rest_framework import serializers
from .models import Payment, PaymentMethod, Transaction, Refund
from orders.serializers import OrderListSerializer

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    
    order = OrderListSerializer(read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('order', 'amount', 'currency', 'created_at', 'updated_at')

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('order', 'payment_method', 'amount', 'currency')

    def validate(self, attrs):
        order = attrs['order']
        if order.payment.exists():
            raise serializers.ValidationError("Payment already exists for this order.")
        return attrs