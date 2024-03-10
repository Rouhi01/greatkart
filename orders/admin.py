from django.contrib import admin
from .models import Order, OrderProduct, Payment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderProduct)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class OrderAdmin(admin.ModelAdmin):
    pass