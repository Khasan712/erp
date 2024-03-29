import uuid

from django.db import models
from django.db.models import Q
from .enums import NotificationChoices
from api.v1.users.models import User
from api.v1.sourcing.models import (
    SourcingRequest,
    SourcingRequestEvent
)
from api.v1.contracts.models import Contract
from api.v1.suppliers.models import (
    SupplierQuestionary,
)
# Create your models here.


class DateTimeMixin(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class Notification(DateTimeMixin):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_receiver')
    sourcing_e = models.ForeignKey(SourcingRequestEvent, on_delete=models.CASCADE, blank=True, null=True)
    sourcing_r = models.ForeignKey(SourcingRequest, on_delete=models.CASCADE, blank=True, null=True)
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, blank=True, null=True, related_name='contract')
    questionary = models.ForeignKey(SupplierQuestionary, on_delete=models.SET_NULL, null=True)
    # n_choices = models.CharField(max_length=10, choices=NotificationChoices.choices())
    url_path = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    text = models.TextField(blank=True, null=True)


class ChatRoom(DateTimeMixin):
    room_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    partner1 = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='chat_partner1')
    partner2 = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='chat_partner2')
    partner1_last_seen = models.DateTimeField(null=True, blank=True)
    partner2_last_seen = models.DateTimeField(null=True, blank=True)
    class Meta:
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'
        
    def __str__(self):
        return f'{self.partner1.email} - {self.partner2.email}'

    def clean(self):
        the_same_rooms = ChatRoom.objects.select_related('partner1', 'partner2').filter(
            Q(partner1_id=self.partner1.id, partner2_id=self.partner2.id) |
            Q(partner2_id=self.partner1.id, partner1_id=self.partner2.id)
        )
        if the_same_rooms:
            raise ValueError("Error")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Chat(DateTimeMixin):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, related_name='chat_room')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='chat_sender')
    
    message = models.TextField(null=True, blank=True)
    answer_for = models.ForeignKey('self', models.SET_NULL, null=True, blank=True)  # TODO: use this

    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.chat_room}'


class ChatFile(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.SET_NULL, null=True)
    chat_file = models.FileField(upload_to='chat/messages/files')
    
    def __str__(self):
        return f'{self.chat} {self.chat.user.email}'