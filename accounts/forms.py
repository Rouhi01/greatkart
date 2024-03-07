from django import forms
from .models import Account
from django.core.exceptions import ValidationError


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

            # Placeholder
            alist = field.split('_')
            s = ' '.join(i.capitalize() for i in alist)
            self.fields[field].widget.attrs['placeholder'] = f'Enter {s}'

    def clean(self):
        cd = super().clean()
        ps1 = cd.get('password')
        ps2 = cd.get('confirm_password')
        if ps2 != ps1:
            raise forms.ValidationError(
                "Password does not match"
            )

    def clean_email(self):
        new_email = self.cleaned_data['email']
        user = Account.objects.filter(email__exact=new_email).exists()
        if user:
            raise forms.ValidationError(
                "Email has already exists"
            )
        return new_email


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class':'form-control',
        'placeholder':'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder':'Password'
    }))



