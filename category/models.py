from django.db import models
from django.urls import reverse


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    category_slug = models.SlugField(max_length=100, unique=True)
    category_description = models.TextField(max_length=255, blank=True)
    category_image = models.ImageField(upload_to='photos/categories/', blank=True)

    def __str__(self):
        return self.category_name

    def get_absolute_url(self):
        return reverse('store:products_by_category', args=[self.category_slug])

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

