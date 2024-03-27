from django.views import View
from django.shortcuts import render
from store.models import Product
from store.models import ReviewRating


class HomeView(View):
    template_name = 'home.html'
    def setup(self, request, *args, **kwargs):
        self.products_instance = Product.objects.all()
        super().setup(request, *args, **kwargs)
    def get(self, request):
        products = self.products_instance.filter(is_available=True).order_by('created_at')
        for product in products:
            reviews = ReviewRating.objects.filter(product__slug=product.slug, status=True)
        context = {
            'products':products,
            'reviews':reviews
        }
        return render(request, self.template_name, context=context)


