# products/filters.py
import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    # Product defines `base_price` (not `price`) and `is_active` (not `available`).
    min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr='lte')

    # Category uses a slug field; Brand model does not have a slug, so filter by name.
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    brand = django_filters.CharFilter(field_name='brand__name', lookup_expr='iexact')
    tags = django_filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')

    # Filter by whether the product is active
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Product
        fields = ['category', 'brand', 'tags', 'min_price', 'max_price', 'is_active']