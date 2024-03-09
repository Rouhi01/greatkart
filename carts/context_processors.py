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
            cart = Cart.objects.filter(cart_id=scart)
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                cart_items = CartItem.objects.filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)
