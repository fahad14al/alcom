

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings # Recommended way to import the User model

# 1. User (extend AbstractUser)
# Use 'class User(AbstractUser):' if you are defining this in a new app
# and setting AUTH_USER_MODEL to 'your_app.User' in settings.py.
# If you are NOT changing AUTH_USER_MODEL but still need an 'extension',
# you'd use a OneToOneField on the UserProfile model.
# Assuming you ARE extending AbstractUser:

class User(AbstractUser):
    """
    Extends the default Django AbstractUser.
    Add any custom fields or methods specific to your main User object here.
    If you modify this, you MUST set AUTH_USER_MODEL = 'your_app_name.User' 
    in your settings.py before running initial migrations.
    """
    # Example custom field
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set_permissions",
        related_query_name="user",
    )

    def __str__(self):
        return self.email or self.username

# ---

# 2. UserProfile (One-to-One with User)
class UserProfile(models.Model):
    """
    Stores additional user information not placed directly on the User model.
    It has a One-to-One relationship with the User model.
    """
    # Use settings.AUTH_USER_MODEL for a Foreign Key/OneToOneField relationship
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # You might consider moving the Address logic here or keeping it separate.
    # For flexibility (multiple addresses), keeping Address separate is better.

    def __str__(self):
        return f"Profile for {self.user.username}"

# ---

# 3. Address (for shipping/billing)
class Address(models.Model):
    """
    Stores a generic address that can be used for shipping or billing.
    A user can have multiple addresses.
    """
    # Use settings.AUTH_USER_MODEL
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    # Fields for the address itself
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Flags to denote the address type
    is_shipping = models.BooleanField(default=True)
    is_billing = models.BooleanField(default=False)
    
    # Optional: A label for the address (e.g., 'Home', 'Work')
    label = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.label or 'Address'} ({self.user.username})"

# ---

# 4. Wishlist
class Wishlist(models.Model):
    """
    A list of items a user wants to purchase.
    It is associated with a specific User.
    """
    # Use settings.AUTH_USER_MODEL
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # M2M Field: Items will be linked via a separate model (e.g., Product)
    # Assuming a 'Product' model exists in your application
    # from your_app.models import Product 
    # items = models.ManyToManyField(Product, related_name='wishlists')

    def __str__(self):
        return f"Wishlist for {self.user.username}"