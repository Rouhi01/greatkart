from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'category_slug': ['category_name',]}
    list_display = ['category_name', 'category_slug']
    list_display_links = ['category_name', 'category_slug']


