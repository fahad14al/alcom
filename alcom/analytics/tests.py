# analytics/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from products.models import Category, Product, Brand
from orders.models import Order, OrderItem
from .models import PageView, ProductView, SalesReport

User = get_user_model()

class PageViewModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='pagetest',
            email='page@example.com',
            password='testpass123'
        )

    def test_create_page_view(self):
        """Test creating a page view"""
        page_view = PageView.objects.create(
            user=self.user,
            page_url='/products/',
            page_title='Products Page',
            session_id='test-session-123',
            ip_address='192.168.1.1',
            user_agent='Test Browser'
        )
        self.assertEqual(str(page_view), 'page@example.com - /products/')
        self.assertEqual(page_view.page_url, '/products/')
        self.assertEqual(page_view.user_agent, 'Test Browser')

    def test_page_view_anonymous_user(self):
        """Test creating page view for anonymous user"""
        page_view = PageView.objects.create(
            page_url='/',
            page_title='Home Page',
            session_id='anonymous-session-456',
            ip_address='192.168.1.2'
        )
        self.assertIsNone(page_view.user)
        self.assertEqual(page_view.page_title, 'Home Page')

    def test_page_view_timestamps(self):
        """Test page view created_at and updated_at timestamps"""
        page_view = PageView.objects.create(
            page_url='/test/',
            session_id='test-session'
        )
        
        self.assertIsNotNone(page_view.created_at)
        self.assertIsNotNone(page_view.updated_at)
        # created_at and updated_at might differ slightly due to processing time
        self.assertAlmostEqual(page_view.created_at, page_view.updated_at, delta=timedelta(seconds=1))

class ProductViewModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='productviewtest',
            email='productview@example.com',
            password='testpass123'
        )
        cls.category = Category.objects.create(name='Test', slug='test')
        cls.brand = Brand.objects.create(name='PVBrand', description='Brand')
        cls.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            base_price=Decimal('99.99'),
            category=cls.category,
            brand=cls.brand,
            is_active=True
        )

    def test_create_product_view(self):
        """Test creating a product view"""
        product_view = ProductView.objects.create(
            user=self.user,
            product=self.product,
            session_id='test-session-789',
            view_duration=30  # 30 seconds
        )
        self.assertEqual(str(product_view), 'productview@example.com - Test Product')
        self.assertEqual(product_view.product.name, 'Test Product')
        self.assertEqual(product_view.view_duration, 30)

    def test_product_view_count_increment(self):
        """Test product view count increments"""
        initial_views = ProductView.objects.filter(product=self.product).count()

        # Create multiple product views
        ProductView.objects.create(product=self.product, session_id='session1')
        ProductView.objects.create(product=self.product, session_id='session2')

        # Confirm via ProductView records
        self.assertEqual(ProductView.objects.filter(product=self.product).count(), initial_views + 2)

    def test_product_view_with_duration(self):
        """Test product view with duration tracking"""
        product_view = ProductView.objects.create(
            product=self.product,
            session_id='duration-session',
            view_duration=120  # 2 minutes
        )
        self.assertEqual(product_view.view_duration, 120)

class SalesReportModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='salestest',
            email='sales@example.com',
            password='testpass123'
        )
        cls.category = Category.objects.create(name='Test', slug='test')
        cls.brand = Brand.objects.create(name='SalesBrand', description='Brand')
        cls.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            base_price=Decimal('50.00'),
            category=cls.category,
            brand=cls.brand,
            is_active=True
        )

    def test_create_sales_report(self):
        """Test creating a sales report"""
        report_date = timezone.now().date()
        sales_report = SalesReport.objects.create(
            report_date=report_date,
            total_revenue=Decimal('1000.00'),
            total_orders=25,
            total_customers=20,
            average_order_value=Decimal('40.00'),
            products_sold=50,
            new_customers=5
        )
        self.assertEqual(str(sales_report), f'Sales Report - {report_date}')
        self.assertEqual(sales_report.total_revenue, Decimal('1000.00'))
        self.assertEqual(sales_report.total_orders, 25)

    def test_sales_report_calculations(self):
        """Test sales report calculated fields"""
        report_date = timezone.now().date()
        sales_report = SalesReport.objects.create(
            report_date=report_date,
            total_revenue=Decimal('2000.00'),
            total_orders=40,
            total_customers=35,
            average_order_value=Decimal('50.00')
        )
        
        # Test conversion rate calculation
        expected_conversion_rate = (40 / 35) * 100 if 35 > 0 else 0
        self.assertEqual(sales_report.conversion_rate, expected_conversion_rate)

    def test_sales_report_unique_date(self):
        """Test that sales report date is unique"""
        report_date = timezone.now().date()
        SalesReport.objects.create(
            report_date=report_date,
            total_revenue=Decimal('500.00'),
            total_orders=10,
            total_customers=5,
            average_order_value=Decimal('50.00')
        )
        
        # Try to create another report with same date
        with self.assertRaises(Exception):
            SalesReport.objects.create(
                report_date=report_date,
                total_revenue=Decimal('600.00'),
                total_orders=12,
                total_customers=6,
                average_order_value=Decimal('50.00')
            )

class AnalyticsManagerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='analyticstest',
            email='analytics@example.com',
            password='testpass123'
        )
        cls.category = Category.objects.create(name='Test', slug='test')
        cls.brand = Brand.objects.create(name='AnalyticsBrand', description='Brand')
        cls.product = Product.objects.create(
            name='Analytics Product',
            slug='analytics-product',
            base_price=Decimal('75.00'),
            category=cls.category,
            brand=cls.brand,
            is_active=True
        )
        
        # Create test data for different dates
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        
        # Create page views
        # Use update to force created_at change for auto_now_add fields
        p1 = PageView.objects.create(page_url='/', session_id='1')
        PageView.objects.filter(pk=p1.pk).update(created_at=timezone.make_aware(datetime.combine(today, datetime.min.time())))
        
        p2 = PageView.objects.create(page_url='/products/', session_id='2')
        PageView.objects.filter(pk=p2.pk).update(created_at=timezone.make_aware(datetime.combine(yesterday, datetime.min.time())))
        
        # Create product views
        pv1 = ProductView.objects.create(product=cls.product, session_id='3')
        ProductView.objects.filter(pk=pv1.pk).update(created_at=timezone.make_aware(datetime.combine(today, datetime.min.time())))
        
        pv2 = ProductView.objects.create(product=cls.product, session_id='4')
        ProductView.objects.filter(pk=pv2.pk).update(created_at=timezone.make_aware(datetime.combine(last_week, datetime.min.time())))

    def test_get_page_views_today(self):
        """Test getting page views for today"""
        today_views = PageView.objects.get_today_views()
        self.assertEqual(today_views.count(), 1)
        self.assertEqual(today_views.first().page_url, '/')

    def test_get_product_views_today(self):
        """Test getting product views for today"""
        today_views = ProductView.objects.get_today_views()
        self.assertEqual(today_views.count(), 1)
        self.assertEqual(today_views.first().product.name, 'Analytics Product')

    def test_get_popular_products(self):
        """Test getting most viewed products"""
        # Create more views for a different product
        popular_brand = Brand.objects.create(name='PopularBrand', description='Brand')
        product2 = Product.objects.create(
            name='Popular Product',
            slug='popular-product',
            base_price=Decimal('100.00'),
            category=self.category,
            brand=popular_brand,
            is_active=True
        )
        ProductView.objects.create(product=product2, session_id='5')
        ProductView.objects.create(product=product2, session_id='6')
        ProductView.objects.create(product=product2, session_id='7') # 3 views
        
        popular_products = ProductView.objects.get_popular_products(limit=2)
        self.assertEqual(popular_products.count(), 2)
        # product2 should be first since it has more views
        self.assertEqual(popular_products.first().name, 'Popular Product')

class PageViewAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='pageviewapi',
            email='pageviewapi@example.com',
            password='testpass123'
        )
        
        # Create test page views
        PageView.objects.create(
            user=cls.user,
            page_url='/products/',
            page_title='Products',
            session_id='session-123'
        )
        PageView.objects.create(
            page_url='/',
            page_title='Home',
            session_id='session-456'
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_track_page_view(self):
        """Test tracking a page view via API"""
        url = '/api/analytics/page-views/'
        data = {
            'page_url': '/test-page/',
            'page_title': 'Test Page',
            'session_id': 'test-session-789',
            'ip_address': '192.168.1.100',
            'user_agent': 'Test Client'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PageView.objects.count(), 3)
        
        new_page_view = PageView.objects.get(page_url='/test-page/')
        self.assertEqual(new_page_view.page_title, 'Test Page')
        self.assertEqual(new_page_view.user, self.user)

    def test_track_page_view_unauthenticated(self):
        """Test tracking page view without authentication"""
        self.client.force_authenticate(user=None)
        
        url = '/api/analytics/page-views/'
        data = {
            'page_url': '/public-page/',
            'page_title': 'Public Page',
            'session_id': 'anonymous-session'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        page_view = PageView.objects.get(page_url='/public-page/')
        self.assertIsNone(page_view.user)

    def test_list_page_views_admin_only(self):
        """Test that only staff users can list page views"""
        url = '/api/analytics/page-views/'
        response = self.client.get(url)
        # Regular users should not be able to list all page views
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_page_views_as_admin(self):
        """Test listing page views as admin user"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=admin_user)
        
        url = '/api/analytics/page-views/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

class ProductViewAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='productviewapi',
            email='productviewapi@example.com',
            password='testpass123'
        )
        cls.category = Category.objects.create(name='Test', slug='test')
        cls.brand = Brand.objects.create(name='PVAPI', description='Brand')
        cls.product = Product.objects.create(
            name='API Test Product',
            slug='api-test-product',
            base_price=Decimal('89.99'),
            category=cls.category,
            brand=cls.brand,
            is_active=True
        )
        
        # Create test product views
        ProductView.objects.create(
            user=cls.user,
            product=cls.product,
            session_id='session-111',
            view_duration=45
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_track_product_view(self):
        """Test tracking a product view via API"""
        url = '/api/analytics/product-views/'
        data = {
            'product': self.product.id,
            'session_id': 'new-session-222',
            'view_duration': 60
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify product view count was incremented via ProductView records
        self.assertEqual(ProductView.objects.filter(product=self.product).count(), 2)

    def test_track_product_view_with_duration(self):
        """Test tracking product view with duration"""
        url = '/api/analytics/product-views/'
        data = {
            'product': self.product.id,
            'session_id': 'duration-session',
            'view_duration': 120  # 2 minutes
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        product_view = ProductView.objects.get(session_id='duration-session')
        self.assertEqual(product_view.view_duration, 120)

    def test_track_product_view_invalid_product(self):
        """Test tracking view for non-existent product"""
        url = '/api/analytics/product-views/'
        data = {
            'product': 999,  # Non-existent product ID
            'session_id': 'invalid-session'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class SalesReportAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='salesreportuser',
            email='salesreport@example.com',
            password='testpass123'
        )
        cls.admin_user = User.objects.create_superuser(
            username='salesadmin',
            email='salesadmin@example.com',
            password='adminpass123'
        )
        
        # Create test sales reports
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        SalesReport.objects.create(
            report_date=today,
            total_revenue=Decimal('1500.00'),
            total_orders=30,
            total_customers=25,
            average_order_value=Decimal('50.00')
        )
        SalesReport.objects.create(
            report_date=yesterday,
            total_revenue=Decimal('800.00'),
            total_orders=16,
            total_customers=14,
            average_order_value=Decimal('50.00')
        )

    def setUp(self):
        self.client = APIClient()

    def test_list_sales_reports_admin_only(self):
        """Test that only admins can list sales reports"""
        self.client.force_authenticate(user=self.user)
        url = '/api/analytics/sales-reports/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_sales_reports_as_admin(self):
        """Test listing sales reports as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/analytics/sales-reports/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_get_sales_report_detail(self):
        """Test retrieving sales report detail"""
        self.client.force_authenticate(user=self.admin_user)
        report = SalesReport.objects.first()
        
        url = f'/api/analytics/sales-reports/{report.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_revenue'], '1500.00')
        self.assertEqual(response.data['total_orders'], 30)

    def test_create_sales_report_admin_only(self):
        """Test that only admins can create sales reports"""
        self.client.force_authenticate(user=self.user)
        url = '/api/analytics/sales-reports/'
        data = {
            'report_date': '2024-01-01',
            'total_revenue': '1000.00',
            'total_orders': 20
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_daily_report(self):
        """Test generating daily sales report"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create some orders for today
        user1 = User.objects.create_user(username='customer1', email='customer1@example.com', password='pass123')
        user2 = User.objects.create_user(username='customer2', email='customer2@example.com', password='pass123')
        
        category = Category.objects.create(name='Test', slug='test')
        report_brand = Brand.objects.create(name='ReportBrand', description='Brand')
        product = Product.objects.create(
            name='Report Product',
            slug='report-product',
            base_price=Decimal('100.00'),
            category=category,
            brand=report_brand,
            is_active=True
        )
        
        # Create orders
        order1 = Order.objects.create(user=user1, total_amount=Decimal('200.00'))
        order2 = Order.objects.create(user=user2, total_amount=Decimal('150.00'))
        OrderItem.objects.create(order=order1, product=product, quantity=2, price_at_purchase=Decimal('100.00'))
        OrderItem.objects.create(order=order2, product=product, quantity=1, price_at_purchase=Decimal('150.00'))
        
        url = '/api/analytics/generate-daily-report/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('report_generated' in response.data)
        self.assertTrue('total_revenue' in response.data)

class AnalyticsDashboardAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            username='dashboardadmin',
            email='dashboard@example.com',
            password='adminpass123'
        )
        
        # Create test data for dashboard
        cls.category = Category.objects.create(name='Test', slug='test')
        cls.brand = Brand.objects.create(name='DashboardBrand', description='Brand')
        cls.product = Product.objects.create(
            name='Dashboard Product',
            slug='dashboard-product',
            base_price=Decimal('75.00'),
            category=cls.category,
            brand=cls.brand,
            is_active=True
        )
        
        # Create page views
        for i in range(5):
            PageView.objects.create(
                page_url=f'/page-{i}/',
                session_id=f'session-{i}'
            )
        
        # Create product views
        for i in range(3):
            ProductView.objects.create(
                product=cls.product,
                session_id=f'product-session-{i}',
                view_duration=30 * (i + 1)
            )
        
        # Create sales reports
        today = timezone.now().date()
        for i in range(7):
            report_date = today - timedelta(days=i)
            SalesReport.objects.create(
                report_date=report_date,
                total_revenue=Decimal('1000.00') + Decimal(str(i * 100)),
                total_orders=20 + i,
                total_customers=18 + i,
                average_order_value=Decimal('50.00')
            )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_get_dashboard_stats(self):
        """Test getting dashboard statistics"""
        url = '/api/analytics/dashboard-stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('total_page_views' in response.data)
        self.assertTrue('total_product_views' in response.data)
        self.assertTrue('total_revenue' in response.data)
        self.assertTrue('total_orders' in response.data)
        
        self.assertEqual(response.data['total_page_views'], 5)
        self.assertEqual(response.data['total_product_views'], 3)

    def test_get_trending_products(self):
        """Test getting trending products"""
        # Create a more popular product
        popular_brand = Brand.objects.create(name='PopularBrand2', description='Brand')
        popular_product = Product.objects.create(
            name='Popular Product',
            slug='popular-product',
            base_price=Decimal('120.00'),
            category=self.category,
            brand=popular_brand,
            is_active=True
        )
        
        # Add more views to popular product
        for i in range(5):
            ProductView.objects.create(
                product=popular_product,
                session_id=f'popular-session-{i}'
            )
        
        url = '/api/analytics/trending-products/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Popular product should be first
        self.assertEqual(response.data[0]['name'], 'Popular Product')
        expected_count = ProductView.objects.filter(product=popular_product).count()
        self.assertEqual(response.data[0]['view_count'], expected_count)

    def test_get_revenue_analytics(self):
        """Test getting revenue analytics data"""
        url = '/api/analytics/revenue-analytics/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('daily_revenue' in response.data)
        self.assertTrue('weekly_trend' in response.data)
        self.assertTrue('monthly_summary' in response.data)

    def test_get_user_behavior_analytics(self):
        """Test getting user behavior analytics"""
        url = '/api/analytics/user-behavior/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('average_session_duration' in response.data)
        self.assertTrue('page_views_per_session' in response.data)
        self.assertTrue('conversion_rate' in response.data)

    def test_dashboard_access_regular_user(self):
        """Test that regular users cannot access dashboard"""
        regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=regular_user)
        
        url = '/api/analytics/dashboard-stats/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
