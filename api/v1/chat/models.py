from django.db import models

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
    
    


class Chat(DateTimeMixin):
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='chat_sender')
    receiver = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='chat_receiver')

    sender_last_seen = models.DateTimeField(null=True, blank=True)
    receiver_last_seen = models.DateTimeField(null=True, blank=True)
    
    message = models.TextField(null=True, blank=True)
    answer_for = models.ForeignKey('self', models.DO_NOTHING, null=True, blank=True)  # TODO: use this

    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.sender.email} with {self.receiver.email}'


# Personal (1to1)
class ChatPersonal(DateTimeMixin, models.Model):
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='receiver')

    sender_last_seen = models.DateTimeField(null=True, blank=True)
    receiver_last_seen = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    @property
    def get_last_message(self):
        message = self.chatmessage_set.last()
        if message:
            return {
                "id": message.id,
                "creator": message.get_creator,
                "text": message.message,
                "is_read": message.is_read,
                "created_at": message.time_created,
                "files": [file.file.url for file in message.chatmessagefile_set.all()],
            }
        return None

    @property
    def get_last_message_time(self):
        last_message = self.chatmessage_set.filter(is_active=True).last()
        if last_message is not None:
            return last_message.time_created
        return self.time_created

    @property
    def unread_messages_count(self):
        return self.chatmessage_set.filter(is_active=True, is_read=False).count()

    def __str__(self): return f"{ self.sender.first_name } { self.sender.last_name } -> { self.receiver.first_name } { self.receiver.last_name }"
    
    

# Messages
class ChatMessage(DateTimeMixin, models.Model):
    LIST_MESSAGE_PERSONAL_CREATOR = (
        ('sender', 'Sender'),
        ('receiver', 'Receiver'),
    )

    chat_personal = models.ForeignKey(ChatPersonal, models.CASCADE, null=True, blank=True)
    chat_personal_message_creator = models.ForeignKey("users.User", models.CASCADE, null=True, blank=True)
    answer_for = models.ForeignKey('self', models.DO_NOTHING, null=True, blank=True)  # TODO: use this

    is_read = models.BooleanField(default=False)

    message = models.TextField()
    is_active = models.BooleanField(default=True)

    @property
    def get_chat_id(self):
        if self.chat_personal:
            return self.chat_personal.id
        return None

    @property
    def get_receivers_id(self):
        if self.chat_personal:
            if self.chat_personal_message_creator_id != self.chat_personal.sender_id:
                return (self.chat_personal.sender_id, ) 
            return self.chat_personal.receiver_id
        return None

    @property
    def get_sender_user(self):
        return self.chat_personal.sender if self.chat_personal_message_creator_id != self.chat_personal.sender_id else self.chat_personal.receiver

    @property
    def get_receiver_user(self):
        return self.chat_personal.sender if self.chat_personal_message_creator_id == self.chat_personal.receiver_id else self.chat_personal.receiver

    def __str__(self):
        if self.chat_personal:
            return f"Personal: { self.chat_personal.id }"

    @property
    def get_creator(self):
        if self.chat_personal and self.chat_personal_message_creator:
            return self.chat_personal_message_creator.get_short_data
        else:
            return {}

    @property
    def get_files(self):
        return []
    
    
class ChatFile(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.SET_NULL, null=True)
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True)
    chat_file = models.FileField(upload_to='chat/messages/files')