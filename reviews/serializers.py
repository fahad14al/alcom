# reviews/serializers.py
from rest_framework import serializers
from .models import Review, Rating
from products.serializers import ProductListSerializer
from accounts.serializers import UserSerializer

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    helpful_count = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('user', 'helpful_count', 'created_at', 'updated_at')

    def get_helpful_count(self, obj):
        return obj.helpful_votes.count()

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        # To create a Review we require an existing Rating instance.
        fields = ('rating', 'title', 'comment')

    def validate(self, attrs):
        request_user = self.context['request'].user
        rating = attrs.get('rating')
        # Ensure the rating exists and belongs to the requesting user
        if rating is None:
            raise serializers.ValidationError({'rating': 'Rating is required.'})
        if rating.user != request_user:
            raise serializers.ValidationError('You can only create a review for your own rating.')
        # Ensure a Review for this rating does not already exist
        if Review.objects.filter(rating=rating).exists():
            raise serializers.ValidationError('A review for this rating already exists.')
        return attrs

    def create(self, validated_data):
        # Create the Review linked to the provided Rating
        return Review.objects.create(**validated_data)