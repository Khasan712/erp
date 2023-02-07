from django.db import transaction

from api.v1.chat.notification_models.notifications import FolderOrDocumentAccessNotification
from api.v1.folders.models import GiveAccessToDocumentFolder
from api.v1.users.models import User
from config.celery import app
from celery import shared_task
from django.core.mail import EmailMessage


@app.task()
def folder_or_document_access_notification(creator_id: int, user: int, query_id: int):
    try:
        with transaction.atomic():
            if isinstance(user, int):
                notification = FolderOrDocumentAccessNotification(
                    access_folder_or_document_id=query_id,
                    sender_id=creator_id,
                    receiver_id=user,
                    description=f'You have notification for access folder or document.',
                    text=f'You have access to folder or items.'
                )
                notification.save()
    except Exception as e:
        pass


@shared_task()
def send_shared_link_email(token_and_emails):
    with transaction.atomic():
        for token_and_email in token_and_emails:
            button_style = f"display: inline-block; text-decoration: none; color: white; padding: 20px 50px; " \
                          f"background-color: blue; border-radius: 10px;"
            html_content = f"<a style={button_style} href='www.jmb-inventory-system.com/shared-link/" \
                           f"?token={token_and_email.get('token')}&{token_and_email.get('cart_id')}'>" \
                           f"<button>Folder Or Document</button></a>"
            subject = "You have access for document or folder"
            email = EmailMessage(
                subject=subject,
                body=f'Click the button for see items. \n{html_content}',
                to=[token_and_email.get('email')],
            )
            email.content_subtype = 'html'
            email.send()
