from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Product
from category.models import Category
from carts.models import CartItem, Cart
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


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
            paginator = Paginator(products, per_page=6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()
        else:
            products = self.products_instance.filter(is_available=True).order_by("id")
            paginator = Paginator(products, per_page=6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()

        context = {
            'products': paged_products,
            'product_count':product_count

        }
        return render(request, self.template_name, context=context)

class ProductDetailView(View):
    template_name = 'store/product_detail.html'
    def _cart_id(self, request):
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart
    def get(self, request, category_slug, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=self._cart_id(request), product=product).exists()
        context = {
            'product':product,
            'in_cart':in_cart,
        }
        return render(request, self.template_name, context)


