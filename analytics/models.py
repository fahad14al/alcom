from django.db import models
from django.conf import settings
from products.models import Product

class PageView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    page_url = models.CharField(max_length=255)
    page_title = models.CharField(max_length=255)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.page_url}"

class ProductView(models.Model):
    """
    Tracks views for each product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views', null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True, help_text="Session ID for anonymous users")
    view_duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"{self.user} - {self.product.name}"
        return f"Anonymous - {self.product.name}"

class SalesReport(models.Model):
    report_date = models.DateField(unique=True)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    total_orders = models.PositiveIntegerField()
    total_customers = models.PositiveIntegerField()
    average_order_value = models.DecimalField(max_digits=12, decimal_places=2)
    products_sold = models.PositiveIntegerField(default=0)
    new_customers = models.PositiveIntegerField(default=0)

    @property
    def conversion_rate(self):
        if self.total_customers > 0:
            return (self.total_orders / self.total_customers) * 100
        return 0

    def __str__(self):
        return f"Sales Report - {self.report_date}"
