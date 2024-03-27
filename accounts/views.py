from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import RegistrationForm, LoginForm, UserProfileForm, UserForm
from .models import Account, UserProfile
from orders.models import OrderProduct, Order
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.utils import user_activation, user_pass_reset
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from carts.models import Cart, CartItem
from orders.models import Order



class RegisterView(View):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        context = {
            'form':form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            user = Account.objects.create_user(
                first_name=cd['first_name'],
                last_name=cd['last_name'],
                email=cd['email'],
                username=cd['email'].split('@')[0],
                password=cd['password']
            )
            user.phone_number = cd['phone_number']
            user.save()
            # messages.success(request, 'Email was sent.')
            # User activation
            user_activation(request, cd['email'], user)

            # messages.success(request, 'THank you for registering with us. We have sent you a verification email to your email address. Please verify it.')
            return redirect(f'/accounts/login/?command=verification&email={cd["email"]}')

        context = {
            'form':form
        }
        return render(request, self.template_name, context)


class LoginView(View):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def _cart_id(self, request):
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        try:
            next_url = request.GET.get('next')
            request.session['next_url'] = next_url
        except:
            pass

        form = self.form_class()
        context = {
            'form':form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            email = cd['email']
            password = cd['password']

            user = authenticate(email=email, password=password)
            if user is not None:
                try:
                    cart = Cart.objects.get(cart_id=self._cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_items = CartItem.objects.filter(cart=cart)
                        product_variation = []
                        for item in cart_items:
                            variation = item.variations.all()
                            product_variation.append(list(variation))
                        cart_items = CartItem.objects.filter(user=user)
                        ex_var_list = []
                        id = []
                        for item in cart_items:
                            variation = item.variations.all()
                            ex_var_list.append(list(variation))
                            id.append(item.id)

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()
                            else:
                                cart_items = CartItem.objects.filter(cart=cart)
                                for item in cart_items:
                                    item.user = user
                                    item.save()
                except:
                    pass
                login(request, user)
                try:
                    next_url = request.session.get('next_url')
                    messages.success(request, 'You are now logged in.')
                    return redirect(next_url)
                except:
                    messages.success(request, 'You are now logged in.')
                    return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Invalid login credentials')
                return redirect('accounts:login')
        context = {
            'form':form
        }
        return render(request, self.template_name, context)


class LogoutView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    def get(self, request):
        logout(request)
        messages.success(request, 'You are logged out.')
        return redirect('home')


class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Congratulations! Your account is activated')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid activation link')
            return redirect('accounts:register')


class DashboardView(LoginRequiredMixin, View):
    template_name = 'accounts/dashboard.html'

    def get(self, request):
        orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
        orders_count = orders.count()
        try:
            user_profile = UserProfile.objects.get(user_id=request.user.id)
        except:
            user_profile = None
        context = {
            'orders':orders,
            'orders_count':orders_count,
            'user_profile':user_profile
        }
        return render(request, self.template_name, context)

class MyOrdersView(LoginRequiredMixin, View):
    template_name = 'accounts/my_orders.html'
    def get(self, request):
        orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
        context = {
            'orders':orders
        }
        return render(request, self.template_name, context)


class EditProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/edit_profile.html'
    form_class1 = UserForm
    form_class2 = UserProfileForm

    def setup(self, request, *args, **kwargs):
        self.user_profile = get_object_or_404(UserProfile, user=request.user)
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        user_form = self.form_class1(instance=request.user)
        profile_form = self.form_class2(instance=self.user_profile)
        context = {
            'user_form':user_form,
            'profile_form':profile_form,
            'user_profile':self.user_profile
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)

        user_form = self.form_class1(request.POST, instance=request.user)
        profile_form = self.form_class2(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:edit_profile')
        context = {
            'user_form':user_form,
            'profile_form':profile_form
        }
        return render(request, self.template_name, context)


class PassResetView(View):
    template_name = 'accounts/pass_reset.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'You do not have access to this page')
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST['email']
        user = Account.objects.filter(email=email).exists()
        if user:
            user = Account.objects.get(email__iexact=email)
            user_pass_reset(request, email, user)
            return redirect('accounts:pass_reset_done')

        else:
            messages.error(request, 'Account does not exist.')
            return redirect('accounts:pass_reset')


class PassResetDoneView(View):
    template_name = 'accounts/pass_reset_done.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'You do not have access to this page')
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name)


class PassResetConfirmView(View):
    template_name = 'accounts/pass_reset_confirm.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'You do not have access to this page')
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account.objects.get(pk=uid)
        except (ValueError, Account.DoesNotExist, TypeError, OverflowError):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = uid
            context = {
                'uidb64':uidb64,
                'token':token
            }
            return render(request, self.template_name, context)
        else:
            messages.error(request, 'This link has been expired!')
            return redirect('accounts:login')


    def post(self, request, uidb64, token):
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(id=uid)
            user.set_password(password)
            user.save()
            return redirect('accounts:pass_reset_complete')
        else:
            messages.error(request, 'Password do not match!')
            return render(request, self.template_name)


class PassResetCompleteView(View):
    template_name = 'accounts/pass_reset_complete.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'You do not have access to this page')
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name)


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'accounts/change_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                return redirect('accounts:change_password')
            else:
                messages.error(request, 'Please enter valid current password.')
                return redirect('accounts:change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('accounts:change_password')


class OrderDetailView(LoginRequiredMixin, View):
    template_name = 'accounts/order_detail.html'

    def get(self, request, order_id):
        order_detail = OrderProduct.objects.filter(order__order_number=order_id)
        order = Order.objects.get(order_number=order_id)
        sub_total = 0
        for i in order_detail:
            sub_total += i.product_price * i.quantity
        context = {
            'order_detail': order_detail,
            'order': order,
            'sub_total':sub_total
        }
        return render(request, self.template_name, context)
