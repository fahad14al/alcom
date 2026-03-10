from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from .models import PageView, ProductView, SalesReport
from .serializers import PageViewSerializer, ProductViewSerializer, SalesReportSerializer
from products.models import Product
from orders.models import Order
from decimal import Decimal

class PageViewViewSet(viewsets.ModelViewSet):
    queryset = PageView.objects.all()
    serializer_class = PageViewSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

class ProductViewViewSet(viewsets.ModelViewSet):
    queryset = ProductView.objects.all()
    serializer_class = ProductViewSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

class SalesReportViewSet(viewsets.ModelViewSet):
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['post'], url_path='generate-daily-report')
    def generate_daily_report(self, request):
        today = timezone.now().date()
        orders_today = Order.objects.filter(created_at__date=today)
        
        total_revenue = orders_today.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
        total_orders = orders_today.count()
        total_customers = orders_today.values('user').distinct().count()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0.00')
        
        report, created = SalesReport.objects.update_or_create(
            report_date=today,
            defaults={
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'total_customers': total_customers,
                'average_order_value': avg_order_value,
            }
        )
        
        return Response({
            'report_generated': True,
            'report_date': today,
            'total_revenue': total_revenue,
            'total_orders': total_orders
        })

    @action(detail=False, methods=['get'], url_path='dashboard-stats')
    def dashboard_stats(self, request):
        stats = {
            'total_page_views': PageView.objects.count(),
            'total_product_views': ProductView.objects.count(),
            'total_revenue': SalesReport.objects.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0,
            'total_orders': SalesReport.objects.aggregate(Sum('total_orders'))['total_orders__sum'] or 0,
        }
        return Response(stats)

    @action(detail=False, methods=['get'], url_path='trending-products')
    def trending_products(self, request):
        # We'll use the manager method we implemented
        popular_views = ProductView.objects.get_popular_products(limit=10)
        data = []
        for view in popular_views:
            if view.product:
                data.append({
                    'id': view.product.id,
                    'name': view.product.name,
                    'view_count': ProductView.objects.filter(product=view.product).count()
                })
        return Response(data)

    @action(detail=False, methods=['get'], url_path='revenue-analytics')
    def revenue_analytics(self, request):
        return Response({
            'daily_revenue': [],
            'weekly_trend': [],
            'monthly_summary': []
        })

    @action(detail=False, methods=['get'], url_path='user-behavior')
    def user_behavior(self, request):
        return Response({
            'average_session_duration': 0,
            'page_views_per_session': 0,
            'conversion_rate': 0
        })
