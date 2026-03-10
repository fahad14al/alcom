from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, RatingViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'ratings', RatingViewSet, basename='ratings')

urlpatterns = [
    path('', include(router.urls)),
    # Nested URLs for products
    path('products/<int:product_id>/reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-reviews'),
]