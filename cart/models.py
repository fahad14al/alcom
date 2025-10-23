from django.db import models
from django.conf import settings
from products.models import Product

# 1. Coupon Model
class Coupon(models.Model):
    """
    Represents a discount coupon that can be applied to a cart.
    """
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Discount in percentage (e.g., 10.5)")
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum amount that can be discounted")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.code

# 2. Discount Model
class Discount(models.Model):
    """
    A flexible model for applying discounts, which could be automatic or specific.
    This can be extended for various promotional scenarios.
    """
    description = models.CharField(max_length=255)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="The fixed amount or percentage of the discount")
    is_percentage = models.BooleanField(default=False, help_text="Is the discount a percentage or a fixed amount?")
    is_active = models.BooleanField(default=True)
    
    # If the discount applies to specific products, categories, or users
    # you could add ManyToManyFields here.
    # e.g., applicable_products = models.ManyToManyField(Product)

    def __str__(self):
        return self.description

# 3. Cart Model
class Cart(models.Model):
    """
    Represents a user's shopping cart.
    It can be associated with a logged-in user or an anonymous session.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_id = models.CharField(max_length=40, null=True, blank=True, help_text="Session ID for anonymous users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Applied coupon
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')
    
    # General discount
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Anonymous Cart (Session: {self.session_id})"

# 4. CartItem Model
class CartItem(models.Model):
    """
    Represents an item within a shopping cart.
    Links a Product to a Cart with a specific quantity.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Cart {self.cart.id}"

    @property
    def total_price(self):
        """
        Calculates the total price for this cart item.
        """
        return self.quantity * self.product.price