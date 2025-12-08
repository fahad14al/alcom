from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PageViewViewSet, ProductViewViewSet, SalesReportViewSet, AnalyticsDashboardViewSet

router = DefaultRouter()
router.register(r'page-views', PageViewViewSet, basename='page-views')
router.register(r'product-views', ProductViewViewSet, basename='product-views')
router.register(r'sales-reports', SalesReportViewSet, basename='sales-reports')

urlpatterns = [
    path('', include(router.urls)),
    path('generate-daily-report/', AnalyticsDashboardViewSet.as_view({'post': 'generate_daily_report'}), name='generate-daily-report'),
    path('dashboard-stats/', AnalyticsDashboardViewSet.as_view({'get': 'dashboard_stats'}), name='dashboard-stats'),
    path('trending-products/', AnalyticsDashboardViewSet.as_view({'get': 'trending_products'}), name='trending-products'),
    path('revenue-analytics/', AnalyticsDashboardViewSet.as_view({'get': 'revenue_analytics'}), name='revenue-analytics'),
    path('user-behavior/', AnalyticsDashboardViewSet.as_view({'get': 'user_behavior'}), name='user-behavior'),
]
