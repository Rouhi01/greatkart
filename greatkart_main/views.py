from django.views import View
from django.shortcuts import render
from store.models import Product
class HomeView(View):
    template_name = 'home.html'
    def setup(self, request, *args, **kwargs):
        self.products_instance = Product.objects.all()
        super().setup(request, *args, **kwargs)
    def get(self, request):
        products = self.products_instance.filter(is_available=True)
        context = {
            'products':products
        }
        return render(request, self.template_name, context=context)