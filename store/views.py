from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Product
from category.models import Category


class StoreView(View):
    template_name = 'store/store.html'

    def setup(self, request, *args, **kwargs):
        self.products_instance = Product.objects.all()
        super().setup(request, *args, **kwargs)

    def get(self, request, category_slug=None):
        products = self.products_instance.filter(is_available=True)

        if category_slug is not None:
            category = get_object_or_404(Category, category_slug=category_slug)
            products = products.filter(category=category)

        context = {
            'products': products,
        }
        return render(request, self.template_name, context=context)


