from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def order_received_email(request, order):
    mail_subject = 'Thank you for your order!'
    template_name = 'orders/order_received_email.html'
    message = render_to_string(
        template_name, {
            'user':request.user,
            'order':order,
    })
    to_email = request.user.email
    send_mail = EmailMessage(
        mail_subject,
        message,
        to=[to_email]
    )
    send_mail.send()