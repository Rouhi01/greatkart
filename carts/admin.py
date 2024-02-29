from django.contrib import admin
from .models import CartItem, Cart

@admin.register(Cart)
class Admin(admin.ModelAdmin):
    list_display = ['cart_id', 'created_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'is_active']
