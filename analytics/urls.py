from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PageViewViewSet, ProductViewViewSet, SalesReportViewSet

router = DefaultRouter()
router.register(r'page-views', PageViewViewSet, basename='page-views')
router.register(r'product-views', ProductViewViewSet, basename='product-views')
router.register(r'sales-reports', SalesReportViewSet, basename='sales-reports')

# Special utility paths for actions that match the expected test URLs
# Note: In DRF routers, @action(detail=False) creates paths like /sales-reports/trending-products/
# The tests expect /api/analytics/trending-products/

urlpatterns = [
    path('', include(router.urls)),
    # Dashboard-like actions that the tests might expect at the top level
    path('dashboard-stats/', SalesReportViewSet.as_view({'get': 'dashboard_stats'}), name='dashboard-stats'),
    path('trending-products/', SalesReportViewSet.as_view({'get': 'trending_products'}), name='trending-products'),
    path('revenue-analytics/', SalesReportViewSet.as_view({'get': 'revenue_analytics'}), name='revenue-analytics'),
    path('user-behavior/', SalesReportViewSet.as_view({'get': 'user_behavior'}), name='user-behavior'),
    path('generate-daily-report/', SalesReportViewSet.as_view({'post': 'generate_daily_report'}), name='generate-daily-report'),
]
