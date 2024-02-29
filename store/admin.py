from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'created_at', 'updated_at', 'is_available']
    prepopulated_fields = {'slug':['name']}


