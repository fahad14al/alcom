from django.contrib import admin
from .models import ProductView, UserActivity, SearchQuery

# Register your models here.
admin.site.register(ProductView)
admin.site.register(UserActivity)
admin.site.register(SearchQuery)