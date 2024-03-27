from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.models import CartItem, Cart
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import ReviewRatingForms
from django.contrib import messages
from orders.models import OrderProduct


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
            'product_count':product_count,
        }
        return render(request, self.template_name, context=context)

class ProductDetailView(View):
    template_name = 'store/product_detail.html'
    form_class = ReviewRatingForms

    def _cart_id(self, request):
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart
    def get(self, request, category_slug, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        product_gallery = ProductGallery.objects.filter(product_id=product.id)
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__slug=product_slug)
            form = self.form_class(instance=reviews)
        except:
            form = self.form_class()

        # Show review button if that's bought
        if request.user.is_authenticated:
            try:
                order_product = OrderProduct.objects.filter(user=request.user, product=product).exists()
            except OrderProduct.DoesNotExist:
                order_product = None
        else:
            order_product = None

        # Get all the reviews
        reviews = ReviewRating.objects.filter(product__slug=product_slug, status=True)

        in_cart = CartItem.objects.filter(cart__cart_id=self._cart_id(request), product=product).exists()
        context = {
            'product':product,
            'in_cart':in_cart,
            'form':form,
            'order_product':order_product,
            'reviews':reviews,
            'product_gallery':product_gallery
        }
        return render(request, self.template_name, context)

    def post(self, request, category_slug, product_slug):
        url = request.META.get('HTTP_REFERER')
        product = Product.objects.get(slug=product_slug)
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__slug=product_slug)
            form = self.form_class(request.POST, instance=reviews)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you! your review has been updated')
                return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewRatingForms(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                data = ReviewRating()
                data.subject = cd['subject']
                data.rating = cd['rating']
                data.review = cd['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.user = request.user
                data.product = product
                data.save()
                messages.success(request, 'Thank you! your review has been submitted')
                return redirect(url)




class SearchView(View):
    template_name = 'store/store.html'
    def get(self, request):
        if 'keyword' in request.GET:
            keyword = request.GET['keyword']
            if keyword:
                products = Product.objects.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword)).order_by('-created_at')
                product_count = products.count()
        context = {
            'products':products,
            'product_count':product_count,
        }
        return render(request, self.template_name, context)