from django.contrib import admin
from .models import Product, Variation, ReviewRating


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'created_at', 'updated_at', 'is_available']
    prepopulated_fields = {'slug':['name']}


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'variation_category', 'variation_value', 'is_active']
    list_editable = ['is_active']
    list_filter = ['product', 'variation_category', 'variation_value']


@admin.register(ReviewRating)
class Admin(admin.ModelAdmin):
    pass

