from django.contrib import admin
from .models import Order, OrderItem, ShippingMethod, OrderStatus

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingMethod)
admin.site.register(OrderStatus)