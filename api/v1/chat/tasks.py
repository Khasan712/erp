from django.db import transaction

from api.v1.chat.notification_models.notifications import FolderOrDocumentAccessNotification
from api.v1.folders.models import GiveAccessToDocumentFolder
from api.v1.users.models import User
from config.celery import app
from celery import shared_task


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
