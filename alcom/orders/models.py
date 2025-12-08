from django.db import models
from django.conf import settings
from products.models import Product
# from accounts.models import Address

# 1. OrderStatus Model
class OrderStatus(models.Model):
    """
    Defines the status of an order (e.g., Pending, Shipped, Delivered).
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "Order Statuses"

    def __str__(self):
        return self.name

# 2. ShippingMethod Model
class ShippingMethod(models.Model):
    """
    Defines a shipping method with its associated cost.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (${self.cost})"

# 3. Order Model
class Order(models.Model):
    """
    Represents a customer's order.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    # shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='shipping_orders')
    # billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='billing_orders')
    
    status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True, related_name='orders')
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tracking information
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

# 4. OrderItem Model
class OrderItem(models.Model):
    """
    Represents a single item within an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the product at the time of purchase")

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.id}"

    @property
    def total_price(self):
        return self.quantity * self.price_at_purchase