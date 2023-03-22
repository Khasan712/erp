import uuid

from django.db import models
from api.v1.users.models import User
from api.v1.organization.models import Organization
from django.core.exceptions import ValidationError


class FolderOrDocument(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folder_creator')
    name = models.CharField(max_length=255, blank=True, null=True)
    document = models.FileField(upload_to='Folders/Documents/', blank=True, null=True)
    is_folder = models.BooleanField(default=True)
    is_trashed = models.BooleanField(default=False)
    is_uploaded = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(blank=True, null=True, editable=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.id}: {self.is_folder}'

    def clean(self):
        if self.document:
            self.is_folder = False

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class GiveAccessCart(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_creator')
    out_side_person = models.EmailField(max_length=250, blank=True, null=True)
    access_code = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.creator} {self.out_side_person}"

    # def save(self, *args, **kwargs):
    #     if not self.organization:
    #         print(self.creator.organization.id)
    #         self.organization = self.creator.organization
    #     super().save(*args, **kwargs)


class GiveAccessToDocumentFolder(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_creator')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='access_user')
    folder_or_document = models.ForeignKey(FolderOrDocument, on_delete=models.CASCADE, related_name='access_item')
    shared_link_cart = models.ForeignKey(GiveAccessCart, on_delete=models.CASCADE, blank=True, null=True)
    out_side_person = models.EmailField(max_length=250, blank=True, null=True)
    access_code = models.CharField(max_length=100, blank=True, null=True)
    editable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(blank=True, null=True, editable=False)

    def __str__(self):
        return f'{self.folder_or_document}: {self.editable}'

    def clean(self):
        if (not self.user and not self.out_side_person) or (self.user and self.out_side_person):
            raise ValidationError(
                {
                    'error': 'Select user or enter email.'
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)





