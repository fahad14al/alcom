# reviews/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review, Rating
from .serializers import ReviewSerializer, ReviewCreateSerializer, RatingSerializer
from .permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(approved=True)

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