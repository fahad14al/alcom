from django.contrib import admin
from .models import User, UserProfile, Address, Wishlist

# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(Wishlist)