from django.db import models
from api.v1.users.models import User
from api.v1.organization.models import Organization


class FolderOrDocument(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    document = models.FileField(upload_to='Folders/Documents/', blank=True, null=True)
    is_folder = models.BooleanField(default=True)
    is_trashed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(blank=True, null=True, editable=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.id}: {self.is_folder}'


class GiveAccessToDocumentFolder(models.Model):
    folder_or_document = models.ForeignKey(FolderOrDocument, on_delete=models.CASCADE, blank=True, null=True)
    editable = models.BooleanField(default=False)
    expiration_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(blank=True, null=True, editable=False)

    def __str__(self):
        return f'{self.folder_or_document}: {self.editable}'


class GiveAccessToDocumentFolderUser(models.Model):
    give_access = models.ForeignKey(GiveAccessToDocumentFolder, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name}: {self.give_access}'


