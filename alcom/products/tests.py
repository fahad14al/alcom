# products/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Category, Product, Brand, ProductImage

User = get_user_model()

class CategoryModelTests(TestCase):
    def test_create_category(self):
        """Test creating a category"""
        category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.assertEqual(str(category), 'Electronics')
        self.assertEqual(category.slug, 'electronics')

    def test_category_ordering(self):
        """Test category ordering by name"""
        Category.objects.create(name='Z Category', slug='z-category')
        Category.objects.create(name='A Category', slug='a-category')
        
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, 'A Category')
        self.assertEqual(categories[1].name, 'Z Category')

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.brand = Brand.objects.create(
            name='Test Brand',
            description='Test brand'
        )

    def test_create_product(self):
        """Test creating a product"""
        product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test product description',
            base_price=99.99,
            category=self.category,
            brand=self.brand,
            is_active=True
        )
        self.assertEqual(str(product), 'Test Product')
        self.assertEqual(product.price, 99.99)
        self.assertTrue(product.is_active)

    def test_product_out_of_stock(self):
        """Test product availability when out of stock"""
        product = Product.objects.create(
            name='Out of Stock Product',
            slug='out-of-stock',
            base_price=49.99,
            category=self.category,
            brand=self.brand,
            is_active=False
        )
        self.assertFalse(product.is_active)

class BrandModelTests(TestCase):
    def test_create_brand(self):
        """Test creating a brand"""
        brand = Brand.objects.create(
            name='Nike',
            description='Sportswear brand'
        )
        self.assertEqual(str(brand), 'Nike')

class ProductImageModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test', slug='test')
        self.brand = Brand.objects.create(name='ImageBrand', description='Brand for images')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            base_price=99.99,
            category=self.category,
            brand=self.brand,
            is_active=True
        )

    def test_create_product_image(self):
        """Test creating a product image"""
        # In real scenario, you'd use SimpleUploadedFile for image
        image = ProductImage.objects.create(
            product=self.product,
            alt_text='Test image',
            is_main=True
        )
        self.assertEqual(str(image), f'Image for {self.product.name} (Order: 0)')
        self.assertTrue(image.is_main)

class CategoryAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        Category.objects.create(name='Electronics', slug='electronics')
        Category.objects.create(name='Clothing', slug='clothing')

    def test_list_categories(self):
        """Test listing all categories"""
        url = '/api/products/categories/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_get_category_detail(self):
        """Test retrieving single category"""
        category = Category.objects.get(slug='electronics')
        url = f'/api/products/categories/{category.slug}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')

class ProductAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.brand = Brand.objects.create(
            name='Test Brand',
            description='Test Brand'
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name='Product One',
            slug='product-one',
            base_price=99.99,
            category=self.category,
            brand=self.brand,
            is_active=True
        )
        self.product2 = Product.objects.create(
            name='Product Two',
            slug='product-two', 
            base_price=149.99,
            category=self.category,
            brand=self.brand,
            is_active=False,
        )

    def test_list_products(self):
        """Test listing all products"""
        url = '/api/products/products/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return active products
        self.assertEqual(response.data['count'], 1)

    def test_get_product_detail(self):
        """Test retrieving single product"""
        url = f'/api/products/products/{self.product1.slug}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Product One')
        self.assertEqual(response.data['category_name'], 'Test Category')

    def test_search_products(self):
        """Test product search functionality"""
        url = '/api/products/products/?search=One'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Product One')

    def test_filter_by_category(self):
        """Test filtering products by category"""
        # Create another category
        other_category = Category.objects.create(name='Other', slug='other')
        Product.objects.create(
            name='Other Product',
            slug='other-product',
            base_price=79.99,
            category=other_category,
            brand=self.brand,
            is_active=True
        )
        
        url = f'/api/products/products/?category={self.category.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return products from specified category
        self.assertTrue(all(
            item['category'] == self.category.id for item in response.data['results']
        ))

    def test_price_filtering(self):
        """Test filtering products by price range"""
        url = '/api/products/products/?min_price=50&max_price=100'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Product One')