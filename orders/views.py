from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from carts.models import CartItem
from .forms import OrderForm
from .models import Order
import datetime
from django.contrib import messages


class PlaceOrderView(LoginRequiredMixin, View):
    template_name = 'orders/payments.html'
    def post(self, request, total=0, quantity=0):
        # if the user's cart is empty redirect to store page
        user = request.user
        cart_items = CartItem.objects.filter(user=user)
        cart_items_count = cart_items.count()
        if cart_items_count <= 0:
            return redirect('store:store')

        # Calculate the grand total
        tax = 0
        grand_total = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax

        # Save all the billing information inside Order Table if the info is correct
        form = OrderForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            data = Order()
            data.user = user
            data.first_name = cd['first_name']
            data.last_name = cd['last_name']
            data.phone = cd['phone']
            data.email = cd['email']
            data.address_line_1 = cd['address_line_1']
            data.address_line_2 = cd['address_line_2']
            data.country = cd['country']
            data.state = cd['state']
            data.city = cd['city']
            data.order_note = cd['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            year = int(datetime.date.today().strftime('%Y'))
            month = int(datetime.date.today().strftime('%m'))
            day = int(datetime.date.today().strftime('%d'))
            date = datetime.date(year, month, day)
            current_date = date.strftime('%Y%m%d')
            order_number = current_date + str(data.id)

            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total
            }
            return render(request, self.template_name, context)
        else:
            messages.error(request, 'I do not know but something is wrong!')
            return render(request, 'carts/checkout.html')


class PaymentsView(LoginRequiredMixin, View):
    template_name = 'orders/payments.html'

    def get(self, request):
        return render(request, self.template_name)



