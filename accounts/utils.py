from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def user_activation(request, email, user):
    current_site = get_current_site(request)
    mail_subject = 'Please activate your account'
    template_name = 'accounts/account_verification_email.html'
    message = render_to_string(
        template_name, {
            'user':user,
            'domain':current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user)
    })
    to_email = email
    send_mail = EmailMessage(
        mail_subject,
        message,
        to=[to_email]
    )
    send_mail.send()


def user_pass_reset(request, email, user):
    current_site = get_current_site(request)
    mail_subject = 'Reset Your Password'
    template_name = 'accounts/pass_reset_email.html'
    message = render_to_string(
        template_name, {
            'user':user,
            'domain':current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user)
    })
    to_email = email
    send_mail = EmailMessage(
        mail_subject,
        message,
        to=[to_email]
    )
    send_mail.send()

