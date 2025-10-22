# payments/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentMethodViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-methods')

urlpatterns = [
    path('', include(router.urls)),
]