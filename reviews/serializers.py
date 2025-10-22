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
        fields = ('product', 'rating', 'title', 'comment')

    def validate(self, attrs):
        user = self.context['request'].user
        product = attrs['product']
        
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        
        return attrs