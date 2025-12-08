# accounts/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import UserProfile, Address

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        """Test creating a new user with email and password"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='testuser2',
                email='',
                password='testpass123'
            )

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profiletest',
            email='profile@example.com',
            password='testpass123'
        )

    def test_create_user_profile(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            phone='+1234567890',
            date_of_birth='1990-01-01'
        )
        self.assertEqual(profile.user.username, 'profiletest')
        self.assertEqual(str(profile), 'Profile for profiletest')

class AddressModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='addresstest',
            email='address@example.com',
            password='testpass123'
        )

    def test_create_address(self):
        """Test creating an address"""
        address = Address.objects.create(
            user=self.user,
            street_address='123 Test Street',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US',
            address_type='shipping'
        )
        self.assertEqual(address.user.username, 'addresstest')
        self.assertEqual(str(address), '123 Test Street, Test City, TS 12345')

class UserAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apitestuser',
            email='api@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

    def test_user_registration(self):
        """Test user registration API"""
        url = reverse('rest_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('key' in response.data)

    def test_user_login(self):
        """Test user login API"""
        url = reverse('rest_login')
        data = {
            'username': 'apitestuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('key' in response.data)

    def test_get_user_list_authenticated(self):
        """Test getting user list when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = '/api/accounts/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_list_unauthenticated(self):
        """Test getting user list when not authenticated"""
        url = '/api/accounts/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AddressAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='addresstest',
            email='address@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_address(self):
        """Test creating address via API"""
        url = '/api/accounts/addresses/'
        data = {
            'street_address': '456 API Street',
            'city': 'APICity',
            'state': 'AP',
            'postal_code': '54321',
            'country': 'US',
            'address_type': 'shipping'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(Address.objects.get().street_address, '456 API Street')

    def test_list_addresses(self):
        """Test listing user addresses"""
        # Create test address
        Address.objects.create(
            user=self.user,
            street_address='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US'
        )
        
        url = '/api/accounts/addresses/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
             self.assertEqual(len(response.data['results']), 1)
        else:
             self.assertEqual(len(response.data), 1)