from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from store.models import Product
from .models import CartItem, Cart
from django.core.exceptions import ObjectDoesNotExist
from store.models import Variation


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

    # def get(self, request, product_id):
    #     product = Product.objects.get(id=product_id)
    #     try:
    #         cart = Cart.objects.get(cart_id=self._cart_id(request))
    #     except Cart.DoesNotExist:
    #         cart = Cart.objects.create(
    #             cart_id=self._cart_id(request)
    #         )
    #     cart.save()
    #     try:
    #         cart_item = CartItem.objects.get(product=product, cart=cart)
    #         cart_item.quantity += 1
    #         cart_item.save()
    #     except CartItem.DoesNotExist:
    #         cart_item = CartItem.objects.create(
    #             product=product,
    #             cart=cart,
    #             quantity=1
    #         )
    #         cart_item.save()
    #     return redirect('carts:cart')

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        product_variation = []
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_value__iexact=value, variation_category__iexact=key)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass
        try:
            cart = Cart.objects.get(cart_id=self._cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=self._cart_id(request)
            )
        cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, cart=cart, quantity=1)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('carts:cart')





class RemoveCartView(View):
    def _cart_id(self, request):
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart

    def get(self, request, product_id, cart_item_id):
        cart = Cart.objects.get(cart_id=self._cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass
        return redirect('carts:cart')


class RemoveCartItemView(View):

    def _cart_id(self, request):
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart

    def get(self, request, product_id, cart_item_id):
        cart = Cart.objects.get(cart_id=self._cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
        return redirect('carts:cart')
