from django.db import models
from django.conf import settings
# from orders.models import Order

# 1. PaymentMethod Model
class PaymentMethod(models.Model):
    """
    Stores different payment methods available (e.g., Credit Card, PayPal).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# 2. Payment Model
class Payment(models.Model):
    """
    Represents a payment for an order.
    """
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    # order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} for Order {self.order.id}"

# 3. Transaction Model
class Transaction(models.Model):
    """
    Logs all payment-related transactions.
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True, help_text="From payment gateway")
    is_success = models.BooleanField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    response_data = models.JSONField(null=True, blank=True, help_text="Raw response from gateway")

    def __str__(self):
        return f"Transaction {self.transaction_id} for Payment {self.payment.id}"

# 4. Refund Model
class Refund(models.Model):
    """
    Stores information about a refund for an order.
    """
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    reason = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='PENDING') # e.g., PENDING, APPROVED, REJECTED
    timestamp = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund of {self.amount} for Order {self.order.id}"