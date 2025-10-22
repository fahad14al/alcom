# orders/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ShippingMethodViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'shipping-methods', ShippingMethodViewSet, basename='shipping-methods')

urlpatterns = [
    path('', include(router.urls)),
]