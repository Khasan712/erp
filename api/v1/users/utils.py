from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db import transaction

from api.v1.sourcing.models import SourcingRequestEvent
from django.conf import settings
from api.v1.users.models import User
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from api.v1.suppliers.models import Supplier
import os


class Utils:
    @staticmethod
    def send_email(user_data, absurl):
        body = f"Hi {user_data.get('first_name')}. Your company has successfully created. \nCompany name {user_data.get('organization_name')} \nPlease verify your email using this link \n{absurl}"
        user_login = f"Login: {user_data.get('email')}"
        user_password = f"Password: {user_data.get('password')}"
        email = EmailMessage(
            body=f"{body} \n{user_login} \n{user_password}",
            subject=f"Congratulations your company has successfully registered.",
            to=[user_data.get('email')],
        )
        email.send()

    @staticmethod
    def send_shared_link_email(token_and_emails):
        with transaction.atomic():
            for token_and_email in token_and_emails:
                button_style = f"display: inline-block; text-decoration: none; color: white; padding: 20px 50px; " \
                              f"background-color: blue; border-radius: 10px;"
                html_content = f"<a style={button_style} href='www.jmb-inventory-system.com/shared-link/" \
                               f"token={token_and_email.get('token')}'><button>Folder Or Document</button></a>"
                subject = "You have access for document or folder"
                email = EmailMessage(
                    subject=subject,
                    body=f'Click the button for see items. \n{html_content}',
                    to=[token_and_email.get('email')],
                )
                email.content_subtype = 'html'
                email.send()


def send_message_to_suppliers(request, suppliers, sourcing_event):
    sourcing_event = SourcingRequestEvent.objects.get(id=sourcing_event)
    current_site = get_current_site(request).domain
    relative_link = reverse('event-detail',args=[sourcing_event.id])
    if settings.DEBUG:
        url_path = f'http://{current_site}{relative_link}'
    else:
        url_path = f'http://{current_site}{relative_link}'

    for supplier in suppliers:
        user_supplier = Supplier.objects.get(id=supplier.get('supplier'))
        supplier = User.objects.get(id=user_supplier.supplier.id)
        token = RefreshToken.for_user(supplier).access_token
        body = f"Hi {supplier.first_name}. You have sourcing event. \n{url_path}?token={str(token)}"
        email = EmailMessage(
            body=f"{body}",
            subject=f"Sourcing event.",
            to=[supplier.email],
        )
        email.send()


def send_message_register(request, user_data):
    user = User.objects.get(email=user_data.get('email'))
    token = RefreshToken.for_user(user).access_token
    if settings.DEBUG:
        absurl = f'http://127.0.0.1:8000/email/verify/?token={token}'
    else:
        absurl = f'{os.environ.get("SITE_DOMAIN")}/email/verify/?token={token}'

    body = f"<h1>Hi {user_data.get('first_name')}. You have successfully registered by " \
           f"{user_data.get('organization_name')} Organization. Please verify your email.</h1>"

    login_password = f"<p>Login: {user_data.get('email')}</p>" \
                     f"<p>Password: {user_data.get('password')}</p>"

    button_style = f"display: inline-block; text-decoration: none; color: white; padding: 20px 50px; " \
                   f"background-color: blue; border-radius: 10px;"

    html_content = f"<a style={button_style} href='{absurl}'><button>Verify your email</button></a>"

    subject = "Congratulations."
    text_body = f'{body} \n{login_password}'
    to = [user_data.get('email')]

    email = EmailMessage(
        body=f'{text_body} \n{html_content}',
        subject=subject,
        to=to
    )
    email.content_subtype = 'html'
    email.send()


def send_email_for_contract_notice(user_email):
    email = EmailMessage(
        body="Working",
        subject="Congratulations.",
        to=[user_email],
    )
    email.send()


def send_email_fixed(user_email, pk):
    user = User.objects.get(email=user_email)
    token = RefreshToken.for_user(user).access_token
    relative_link = reverse('contract-detail')
    if settings.DEBUG:
        contract_path = f'http://localhost:8000/?contract={pk}&token={token}'
    else:
        contract_path = f'http://jmb-inventory-system.com/?contract={pk}&token={token}'
    email = EmailMessage(
        body=f"Your contract expired, Contract status EXPIRED. \n{contract_path}",
        subject="Your contract expired.",
        to=[user_email],
    )
    email.send()


def send_email_auto_renew(user_email, expiration_date, pk):
    user = User.objects.get(email=user_email)
    token = RefreshToken.for_user(user).access_token
    relative_link = reverse('contract-detail')
    if settings.DEBUG:
        contract_path = f'http:localhost:8000/?contract={pk}&token={token}'
    else:
        contract_path = f'http://jmb-inventory-system.com/?contract={pk}&token={token}'
    email = EmailMessage(
        body=f"Contract has successfully auto renewed. Next expiration date is {expiration_date}. \n{contract_path}",
        subject="Contract has successfully auto renewed.",
        to=[user_email],
    )
    email.send()
