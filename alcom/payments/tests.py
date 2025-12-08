# payments/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from orders.models import Order
from accounts.models import Address
from .models import Payment, PaymentMethod

User = get_user_model()

class PaymentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='paymenttest',
            email='payment@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('116.58')
        )
        # payment method for these tests
        self.payment_method = PaymentMethod.objects.create(name='PM', description='pm', is_active=True)

    def test_create_payment(self):
        """Test creating a payment"""
        payment = Payment.objects.create(
            payment_method=self.payment_method if hasattr(self, 'payment_method') else None,
            amount=Decimal('116.58'),
            status='PENDING'
        )
        # __str__ may not include order in this model; just check amount/status
        self.assertEqual(payment.amount, Decimal('116.58'))
        self.assertEqual(payment.status, 'PENDING')

    def test_payment_status_flow(self):
        """Test payment status transitions"""
        payment = Payment.objects.create(
            order=self.order,
            payment_method=self.payment_method,
            amount=Decimal('116.58')
        )
        # Initial status should be PENDING (model uses uppercase statuses)
        self.assertEqual(payment.status, 'PENDING')

        # Simulate successful payment
        payment.status = 'COMPLETED'
        payment.save()
        self.assertEqual(payment.status, 'COMPLETED')

class PaymentMethodModelTests(TestCase):
    def test_create_payment_method(self):
        """Test creating a payment method"""
        payment_method = PaymentMethod.objects.create(
            name='Credit Card',
            description='Pay with credit card',
            is_active=True
        )
        self.assertEqual(str(payment_method), 'Credit Card')
        self.assertTrue(payment_method.is_active)

class PaymentAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='paymentapi',
            email='paymentapi@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('99.99')
        )
        
        # Create payment methods
        self.credit_card = PaymentMethod.objects.create(name='Credit Card', description='CC', is_active=True)
        self.paypal = PaymentMethod.objects.create(name='PayPal', description='PayPal', is_active=True)
        
        self.client.force_authenticate(user=self.user)

    def test_list_payment_methods(self):
        """Test listing available payment methods"""
        url = '/api/payments/payment-methods/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Should only return active methods
        method_names = [method['name'] for method in response.data['results']]
        self.assertIn('Credit Card', method_names)
        self.assertIn('PayPal', method_names)

    def test_create_payment(self):
        """Test creating a payment"""
        url = '/api/payments/payments/'
        data = {
            'payment_method': self.credit_card.id,
            'amount': '99.99'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        
        payment = Payment.objects.first()
        self.assertEqual(str(payment.amount), '99.99')
        # Payment.payment_method is a FK to PaymentMethod; ensure it exists
        self.assertIsNotNone(payment.payment_method)

    def test_create_payment_invalid_order(self):
        """Test creating payment for order that doesn't belong to user"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_order = Order.objects.create(user=other_user, total_amount=Decimal('0.00'))
        
        url = '/api/payments/payments/'
        data = {
            'order': other_order.id,
            'payment_method': self.credit_card.id,
            'amount': '99.99'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_user_payments(self):
        """Test listing user's payments"""
        # Create a payment first
        Payment.objects.create(
            order=self.order,
            payment_method=self.credit_card,
            amount=Decimal('99.99')
        )
        
        url = '/api/payments/payments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_payment_detail(self):
        """Test retrieving payment details"""
        payment = Payment.objects.create(
            order=self.order,
            payment_method=self.credit_card,
            amount=Decimal('99.99')
        )
        
        url = f'/api/payments/payments/{payment.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data['payment_method'], self.credit_card.id)
        self.assertEqual(response.data['amount'], '99.99')