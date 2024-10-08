from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(request, user):
    print('---------------------')
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    message = render_to_string('verification_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()


def send_mail(subject, mail_template, context):
    message = render_to_string(mail_template, context)
    to_email = context['user'].email
    email = EmailMessage(
        subject, message, to=[to_email]
    )
    email.send()
