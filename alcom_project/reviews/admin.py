from django.contrib import admin
from .models import Rating, Review, ReviewImage

# Register your models here.
admin.site.register(Rating)
admin.site.register(Review)
admin.site.register(ReviewImage)