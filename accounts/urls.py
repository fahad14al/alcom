# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'profiles', UserProfileViewSet, basename='profiles')
router.register(r'addresses', AddressViewSet, basename='addresses')

urlpatterns = [
    path('', include(router.urls)),
]