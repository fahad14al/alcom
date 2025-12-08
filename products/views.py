# products/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage, Brand, Tag
from .serializers import (
    CategorySerializer, ProductListSerializer, 
    ProductDetailSerializer, BrandSerializer,
    TagSerializer, ProductImageSerializer
)
from .filters import ProductFilter

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        category = self.get_object()
        products = category.products.filter(is_active=True)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'tags__name']
    ordering_fields = ['base_price', 'created_at', 'name']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        product = self.get_object()
        similar_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:8]
        serializer = ProductListSerializer(similar_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        # If you later add an `is_featured` field, re-enable filtering by it.
        featured_products = Product.objects.filter(is_active=True)[:12]
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        # 'compare_price' not implemented; for now return active products
        on_sale_products = Product.objects.filter(is_active=True)[:12]
        serializer = self.get_serializer(on_sale_products, many=True)
        return Response(serializer.data)

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer