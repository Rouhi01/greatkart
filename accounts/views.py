from django.shortcuts import render, redirect
from django.views import View
from .forms import RegistrationForm, LoginForm
from .models import Account
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin


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
            messages.success(request, 'Registration successful.')
            return redirect('accounts:register')

        context = {
            'form':form
        }
        return render(request, self.template_name, context)


class LoginView(View):
    template_name = 'accounts/login.html'
    form_class = LoginForm

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
        print(f'{form.errors}')
        if form.is_valid():
            cd = form.cleaned_data
            email = cd['email']
            password = cd['password']

            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                # messages.success(request, 'You are now logged in.')
                return redirect('home')
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