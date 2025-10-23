from django.db import models
from django.conf import settings
# from products.models import Product

# 1. ProductView Model
class ProductView(models.Model):
    """
    Tracks views for each product.
    """
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True, help_text="Session ID for anonymous users")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"{self.product.name} viewed by {self.user.username}"
        return f"{self.product.name} viewed by anonymous user (Session: {self.session_id})"

# 2. UserActivity Model
class UserActivity(models.Model):
    """
    Logs various user actions on the site.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=100) # e.g., 'login', 'logout', 'add_to_cart'
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(null=True, blank=True, help_text="Additional details about the activity")

    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"

# 3. SearchQuery Model
class SearchQuery(models.Model):
    """
    Stores search terms users are looking for.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    results_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.query