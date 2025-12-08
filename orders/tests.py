from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Order, OrderItem, ShippingMethod

User = get_user_model()


class OrdersSmokeTests(TestCase):
    """Lightweight tests adapted to current Order/Shipping models.

    These tests avoid asserting on fields that aren't present in the
    current model definitions and focus on basic creation and relations.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='ordertest', password='pass')
        self.shipping_method = ShippingMethod.objects.create(
            name='Standard', description='Standard', cost=Decimal('5.00'), is_active=True
        )

    def test_create_order_minimal(self):
        order = Order.objects.create(user=self.user, total_amount=Decimal('100.00'))
        self.assertEqual(order.user, self.user)
        self.assertTrue(order.total_amount == Decimal('100.00'))

    def test_orderitem_total_price(self):
        order = Order.objects.create(user=self.user, total_amount=Decimal('0'))
        item = OrderItem.objects.create(order=order, quantity=2, price_at_purchase=Decimal('10.00'))
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

    def test_create_order(self):
        """Test creating an order via API"""
        url = '/api/orders/orders/'
        data = {
            'shipping_method': self.shipping_method.id,
            'total_amount': '150.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get().total_amount, Decimal('150.00'))

    def test_list_orders(self):
        """Test listing user's orders"""
        Order.objects.create(user=self.user, total_amount=Decimal('100.00'))
        Order.objects.create(user=self.user, total_amount=Decimal('200.00'))
        
        url = '/api/orders/orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_order_detail(self):
        """Test retrieving a single order"""
        order = Order.objects.create(user=self.user, total_amount=Decimal('123.45'))
        url = f'/api/orders/orders/{order.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_amount'], '123.45')
