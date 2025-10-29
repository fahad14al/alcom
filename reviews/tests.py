from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Category, Product, Brand
from .models import Rating, Review

User = get_user_model()


class RatingAndReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ratingtest', password='pass')
        self.category = Category.objects.create(name='Test', slug='test')
        self.brand = Brand.objects.create(name='ReviewBrand', description='Brand')
        self.product = Product.objects.create(name='Test Product', slug='test-product', base_price=99.99, category=self.category, brand=self.brand, is_active=True)

    def test_create_rating_and_review(self):
        rating = Rating.objects.create(product=self.product, user=self.user, rating=5)
        self.assertEqual(str(rating), f"5 stars for {self.product.name} by {self.user.username}")

        review = Review.objects.create(rating=rating, title='Great', comment='Nice product', is_approved=True)
        self.assertEqual(str(review), 'Great')
        self.assertTrue(review.is_approved)

    def test_rating_uniqueness_per_user(self):
        Rating.objects.create(product=self.product, user=self.user, rating=4)
        # creating another rating by same user for same product should raise
        with self.assertRaises(Exception):
            Rating.objects.create(product=self.product, user=self.user, rating=5)

class ReviewAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='reviewapi',
            email='reviewapi@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.brand = Brand.objects.create(name='ReviewBrand', description='Brand')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            base_price=99.99,
            category=self.category,
            brand=self.brand,
            is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_review(self):
        """Test creating a review for a product"""
        url = f'/api/reviews/products/{self.product.id}/reviews/'
        data = {
            'rating': 5,
            'title': 'Excellent!',
            'comment': 'I loved this product.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Review.objects.count(), 1)

    def test_list_reviews_for_product(self):
        """Test listing reviews for a specific product"""
        # Create a rating and review
        rating = Rating.objects.create(product=self.product, user=self.user, rating=4)
        Review.objects.create(rating=rating, title='Good', comment='It was okay.')

        url = f'/api/reviews/products/{self.product.id}/reviews/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Good')

    def test_get_review_detail(self):
        """Test retrieving a single review"""
        rating = Rating.objects.create(product=self.product, user=self.user, rating=5)
        review = Review.objects.create(rating=rating, title='Awesome', comment='Really great.')

        url = f'/api/reviews/reviews/{review.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Awesome')
