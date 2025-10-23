# cart/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartItemViewSet, CouponViewSet

router = DefaultRouter()
router.register(r'carts', CartViewSet, basename='carts')
router.register(r'cart-items', CartItemViewSet, basename='cart-items')
router.register(r'coupons', CouponViewSet, basename='coupons')

urlpatterns = [
    path('', include(router.urls)),
]