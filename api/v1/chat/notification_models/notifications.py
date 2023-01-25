from django.core.exceptions import ValidationError
from django.db import models
from api.v1.contracts.models import Contract
from api.v1.folders.models import FolderOrDocument, GiveAccessToDocumentFolder
from api.v1.users.models import User


class ContractNotification(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.receiver.email} - {self.contract.contract_number}'


class FolderOrDocumentAccessNotification(models.Model):
    access_folder_or_document = models.ForeignKey(GiveAccessToDocumentFolder, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invite_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invite_receiver')
    description = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.receiver.email} - {self.access_folder_or_document.access_code}'

    def clean(self):
        if self.access_folder_or_document.creator.id != self.sender.id or self.access_folder_or_document.user.id != self.receiver.id:
            raise ValidationError(
                {
                    'error': 'Error occurred'
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
