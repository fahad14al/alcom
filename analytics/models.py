from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product

class AnalyticsQuerySet(models.QuerySet):
    def get_today_views(self):
        return self.filter(created_at__date=timezone.now().date())

class PageViewManager(models.Manager):
    def get_queryset(self):
        return AnalyticsQuerySet(self.model, using=self._db)
    
    def get_today_views(self):
        return self.get_queryset().get_today_views()

class PageView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    page_url = models.CharField(max_length=255)
    page_title = models.CharField(max_length=255)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PageViewManager()

    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"{user_display} - {self.page_url}"

class ProductViewManager(models.Manager):
    def get_queryset(self):
        return AnalyticsQuerySet(self.model, using=self._db)
    
    def get_today_views(self):
        return self.get_queryset().get_today_views()

    def get_popular_products(self, limit=10):
        from django.db.models import Count, Case, When
        top_products = self.values('product').annotate(
            count=Count('product')
        ).order_by('-count')[:limit]
        
        product_ids = [p['product'] for p in top_products]
        # Preserve order
        preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(product_ids)])
        
        # We need to return ProductView objects for the tests to pass (if they expect views)
        # OR return Product objects if the view expects products.
        # The view uses 'for view in popular_views: if view.product:'
        # So it expects an iterable of objects that have a 'product' attribute.
        
        # Let's return ProductView objects that represent these top products
        # We pick one view per product
        from django.db.models import Max
        view_ids = self.values('product').annotate(
            max_id=Max('id'),
            count=Count('id')
        ).order_by('-count').values_list('max_id', flat=True)[:limit]
        
        # Preserve order in final queryset
        preserved_views = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(view_ids)])
        return self.filter(id__in=view_ids).order_by(preserved_views)

class ProductView(models.Model):
    """
    Tracks views for each product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views', null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True, help_text="Session ID for anonymous users")
    view_duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductViewManager()

    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"{user_display} - {self.product.name if self.product else 'Unknown Product'}"

class SalesReport(models.Model):
    report_date = models.DateField(unique=True)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_customers = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    products_sold = models.PositiveIntegerField(default=0)
    new_customers = models.PositiveIntegerField(default=0)

    @property
    def conversion_rate(self):
        if self.total_customers > 0:
            return (self.total_orders / self.total_customers) * 100
        return 0

    def __str__(self):
        return f"Sales Report - {self.report_date}"

    class Meta:
        ordering = ['-report_date']

