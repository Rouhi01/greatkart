from .models import Cart, CartItem

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            scart = request.session.session_key
            if not scart:
                scart = request.session.create()
            cart = Cart.objects.get(cart_id=scart)
            cart_items = CartItem.objects.filter(cart__cart_id=cart)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)
