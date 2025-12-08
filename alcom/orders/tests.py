from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Order, OrderItem, ShippingMethod
from cart.models import Cart, CartItem
from products.models import Product, Category, Brand

User = get_user_model()


class OrdersSmokeTests(TestCase):
    """Lightweight tests adapted to current Order/Shipping models.

    These tests avoid asserting on fields that aren't present in the
    current model definitions and focus on basic creation and relations.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='ordertest', email='ordertest@example.com', password='pass')
        self.shipping_method = ShippingMethod.objects.create(
            name='Standard', description='Standard', cost=Decimal('5.00'), is_active=True
        )

    def test_create_order_minimal(self):
        order = Order.objects.create(user=self.user, total_amount=Decimal('100.00'))
        self.assertEqual(order.user, self.user)
        self.assertTrue(order.total_amount == Decimal('100.00'))

    def test_orderitem_total_price(self):
        # Need a product to create an order item now
        category = Category.objects.create(name='Test', slug='test')
        brand = Brand.objects.create(name='Brand', description='Desc')
        product = Product.objects.create(name='P', slug='p', base_price=10.00, category=category, brand=brand)
        
        order = Order.objects.create(user=self.user, total_amount=Decimal('0'))
        item = OrderItem.objects.create(order=order, product=product, quantity=2, price_at_purchase=Decimal('10.00'))
        self.assertEqual(item.total_price, Decimal('20.00'))

class OrderAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='orderapi',
            email='orderapi@example.com',
            password='testpass123'
        )
        self.shipping_method = ShippingMethod.objects.create(
            name='Standard', description='Standard', cost=Decimal('5.00'), is_active=True
        )
        self.client.force_authenticate(user=self.user)
        
        # Setup product for tests
        self.category = Category.objects.create(name='Test Cat', slug='test-cat')
        self.brand = Brand.objects.create(name='Test Brand', description='Brand')
        self.product = Product.objects.create(
            name='Test Product', slug='test-product', base_price=75.00,
            category=self.category, brand=self.brand, is_active=True
        )

    def test_create_order(self):
        """Test creating an order via API (checkout)"""
        # Create a cart with items first
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        url = '/api/orders/orders/'
        data = {
            'shipping_method': self.shipping_method.id
            # total_amount is calculated from cart
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        # 2 * 75.00 = 150.00
        self.assertEqual(Order.objects.get().total_amount, Decimal('150.00'))

    def test_list_orders(self):
        """Test listing user's orders"""
        Order.objects.create(user=self.user, total_amount=Decimal('100.00'))
        Order.objects.create(user=self.user, total_amount=Decimal('200.00'))
        
        url = '/api/orders/orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_get_order_detail(self):
        """Test retrieving a single order"""
        order = Order.objects.create(user=self.user, total_amount=Decimal('123.45'))
        url = f'/api/orders/orders/{order.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Compare as strings or Decimal
        self.assertEqual(str(response.data['total_amount']), '123.45')
