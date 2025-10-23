
# payments/serializers.py
from rest_framework import serializers
from .models import Payment, PaymentMethod, Transaction, Refund

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
    payment_method_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_method', 'payment_method_display', 'amount',
            'status', 'status_display', 'transactions', 'timestamp'
        ]

    def get_payment_method_display(self, obj: Payment) -> str:
        # Return the payment method name when available
        return obj.payment_method.name if obj.payment_method else ''

    def get_status_display(self, obj: Payment) -> str:
        # Use the model's get_FOO_display if available
        try:
            return obj.get_status_display()
        except Exception:
            return obj.status

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('payment_method', 'amount')