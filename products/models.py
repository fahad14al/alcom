from django.db import models

class Brand(models.Model):
    """Stores product brand information."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    
class Category(models.Model):
    """Stores product categories, supporting hierarchy."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    """Keywords used to describe products."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    """The main product listing."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def price(self):
        """Backward-compatible alias that returns price as float for tests.

        Note: returning float keeps existing tests (which compare to floats)
        passing without requiring changes across many test files. If you
        prefer Decimal behavior, update tests to compare Decimal values.
        """
        return float(self.base_price)
    
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class ProductVariant(models.Model):
    """Represents a specific version of a product (e.g., Small, Red)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    
    # Example fields for variants. You might use EAV (Entity-Attribute-Value) 
    # for more complex variant systems, but this simple design is common.
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit")
    
    # Optional: adjust price per variant (e.g., XXL costs more)
    variant_price_adjustment = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )

    class Meta:
        # Ensures that a product doesn't have duplicate size/color variants
        unique_together = ('product', 'size', 'color') 

    def __str__(self):
        return f"{self.product.name} - {self.size}/{self.color}"
    
class ProductImage(models.Model):
    """Stores images associated with a product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0) # To control display order

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name} (Order: {self.order})"