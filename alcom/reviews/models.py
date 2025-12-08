from django.db import models
from django.conf import settings
from products.models import Product

# 1. Rating Model
class Rating(models.Model):
    """
    Stores a rating for a product given by a user.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)]) # 1 to 5 stars
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user') # A user can only rate a product once

    def __str__(self):
        return f"{self.rating} stars for {self.product.name} by {self.user.username}"

# 2. Review Model
class Review(models.Model):
    """
    Stores a review for a product, linked to a rating.
    """
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE, related_name='review')
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False, help_text="Approve the review to make it public")

    def __str__(self):
        return self.title

# 3. ReviewImage Model
class ReviewImage(models.Model):
    """
    Stores images associated with a review.
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for review: {self.review.title}"

# 4. ReviewHelpfulVote Model
class ReviewHelpfulVote(models.Model):
    """
    Stores users who found a review helpful.
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return f"{self.user} found review {self.review.id} helpful"