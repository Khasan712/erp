from django.db import transaction
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import (
    GiveAccessToDocumentFolder
)
from datetime import datetime
import uuid


def save_updated_time(instance):
    instance.updated_at = datetime.now()
    instance.save()


@receiver(post_save, sender=GiveAccessToDocumentFolder)
def folder_post_save_signal(sender, instance, created, **kwargs):
    if created:
        instance.access_code = uuid.uuid4()
        instance.save()

# @receiver(post_save, sender=Folder)
# def folder_post_save_signal(sender, instance, created, **kwargs):
#     if created:
#         save_updated_time(instance)
#     else:
#         save_updated_time(instance)
#
#
# @receiver(post_save, sender=Document)
# def document_post_save_signal(sender, instance, created, **kwargs):
#     if created:
#         save_updated_time(instance)
#     elif not created:
#         save_updated_time(instance)
#
#
# @receiver(post_save, sender=GiveAccessToDocumentFolder)
# def give_access_to_someone_post_save_signal(sender, instance, created, **kwargs):
#     if created:
#         save_updated_time(instance)
#     elif not created:
#         save_updated_time(instance)

