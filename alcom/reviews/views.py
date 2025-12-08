from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review, Rating
from products.models import Product
from .serializers import ReviewSerializer, ReviewCreateSerializer, RatingSerializer
from .permissions import IsOwnerOrReadOnly
from django.shortcuts import get_object_or_404

class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        return Review.objects.filter(is_approved=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        review = self.get_object()
        review.helpful_votes.add(request.user)
        return Response({'status': 'marked as helpful'})

    @action(detail=True, methods=['post'])
    def unhelpful(self, request, pk=None):
        review = self.get_object()
        review.helpful_votes.remove(request.user)
        return Response({'status': 'removed helpful vote'})

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProductReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        slug = self.kwargs.get('slug')
        product = get_object_or_404(Product, slug=slug)
        # Return reviews for this product
        return Review.objects.filter(rating__product=product, is_approved=True)

    def create(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        product = get_object_or_404(Product, slug=slug)
        
        # User must be authenticated
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        rating_value = data.get('rating')
        title = data.get('title')
        comment = data.get('comment')

        if not rating_value:
             return Response({'rating': 'Rating is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or Get Rating
        # Check if user already rated
        if Rating.objects.filter(product=product, user=request.user).exists():
             return Response({'detail': 'You have already rated this product.'}, status=status.HTTP_400_BAD_REQUEST)

        rating = Rating.objects.create(
            product=product,
            user=request.user,
            rating=rating_value
        )

        # Create Review
        review = Review.objects.create(
            rating=rating,
            title=title,
            comment=comment,
            is_approved=True # Auto-approve for simplified flow or based on settings
        )
        
        serializer = self.get_serializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)