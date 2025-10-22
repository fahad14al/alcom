from django.contrib import admin
from .models import Payment, PaymentMethod, Transaction, Refund

# Register your models here.
admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(Transaction)
admin.site.register(Refund)