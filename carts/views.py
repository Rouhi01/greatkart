from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from store.models import Product
from .models import CartItem, Cart
from django.core.exceptions import ObjectDoesNotExist


class CartView(View):
    template_name = 'carts/cart.html'
    def _cart_id(self, request):
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart
    def get(self, request, total=0, quantity=0, cart_items=None, tax=0, grand_total=0):
        try:
            cart = Cart.objects.get(cart_id=self._cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
            tax = (2 * total)/100
            grand_total = total + tax
        except ObjectDoesNotExist:
            pass
        context = {
            'total':total,
            'quantity':quantity,
            'cart_items':cart_items,
            'tax':tax,
            'grand_total':grand_total
        }
        return render(request, self.template_name, context)


class AddCartView(View):
    def _cart_id(self, request):
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart

    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        try:
            cart = Cart.objects.get(cart_id=self._cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=self._cart_id(request)
            )
        cart.save()
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )
            cart_item.save()
        return redirect('carts:cart')


class RemoveCartView(View):
    def _cart_id(self, request):
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart

    def get(self, request, product_id):
        cart = Cart.objects.get(cart_id=self._cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('carts:cart')


class RemoveCartItemView(View):

    def _cart_id(self, request):
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart

    def get(self, request, product_id):
        cart = Cart.objects.get(cart_id=self._cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()
        return redirect('carts:cart')
