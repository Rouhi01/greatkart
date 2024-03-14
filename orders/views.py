from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product
import datetime
from django.contrib import messages
import json

from orders.utils import order_received_email
from django.http import JsonResponse


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
        body = json.loads(request.body)
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['order_id'])

        # save transaction details inside Payment table
        payment = Payment(
            user = request.user,
            payment_id=body['transID'],
            payment_method=body['payment_method'],
            amount_paid=order.order_total,
            status=body['status'],
        )
        payment.save()

        # update some field of Order table
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order_id = order.id
            order_product.payment = payment
            order_product.user_id = request.user.id
            order_product.product_id = item.product_id
            order_product.quantity = item.quantity
            order_product.product_price = item.product_price
            order_product.ordered = True
            order_product.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variation)
            order_product.save()

            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # Send order received email to customer
        order_received_email(request, order)

        # Send order number and transaction id back to sendData method via JsonRequest
        data = {
            'order_number':order.order_number,
            'transID':payment.payment_id,
        }
        return JsonResponse(data)


class OrderCompleteView(LoginRequiredMixin, View):
    template_name = 'orders/order_complete.html'

    def get(self, reqeust):
        order_number = reqeust.GET.get('order_number')
        transID = reqeust.GET.get('payment_id')

        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
            ordered_products = OrderProduct.objects.filter(order_id=order.id)
            sub_total = 0
            for item in ordered_products:
                sub_total += item.product_price * item.quantity
            payment = Payment.objects.get(payment_id=transID)
            context = {
                'order':order,
                'ordered_products':ordered_products,
                'order_number':order.order_number,
                'transID':payment.payment_id,
                'payment':payment,
                'sub_total':sub_total
            }
            return render(reqeust, self.template_name, context)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect('home')

    def post(self, request):
        pass