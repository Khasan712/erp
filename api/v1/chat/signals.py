# code
from django.db.models.signals import post_save, pre_delete
from api.v1.sourcing.models import SourcingComments
from django.dispatch import receiver
from .models import Notification
 

@receiver(post_save, sender=SourcingComments)
def create_notification(sender, instance, created, **kwargs):
    if created:
        if instance.sourcingRequestEvent:
            Notification.objects.create(
                sender=instance.author,
                text=f"Commented on: {instance.sourcingRequestEvent.title}",
                receiver=instance.sourcingRequestEvent.creator,
                sourcing_e=instance.sourcingRequestEvent
            )
        if instance.sourcingRequest:
            Notification.objects.create(
                sender=instance.author,
                text=f"Commented on: {instance.sourcingRequest.sourcing_request_name}",
                receiver=instance.sourcingRequest.requestor,
                sourcing_r=instance.sourcingRequest
            )

# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#         instance.profile.save()
