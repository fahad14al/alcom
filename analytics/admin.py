from django.contrib import admin
from .models import ProductView, PageView, SalesReport

# Register your models here.
admin.site.register(ProductView)
admin.site.register(PageView)
admin.site.register(SalesReport)
