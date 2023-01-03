from django.db import models
from .mixins import DocumentFolderMixin
from api.v1.users.models import User
# Create your models here.


class Folder(DocumentFolderMixin):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.creator.first_name}'

    @property
    def get_documents(self):
        pass


class Document(DocumentFolderMixin):
    document = models.FileField(upload_to='Folders/Documents/')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, blank=True, null=True, related_name='document_folder')

    def __str__(self):
        return f'{self.document}'


class GiveAccessToDocumentFolder(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, blank=True, null=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True, null=True)
    editable = models.BooleanField(default=False)
    expiration_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(blank=True, null=True, editable=False)

    def __str__(self):
        return f'{self.folder}: {self.document}: {self.editable}'


class GiveAccessToDocumentFolderUser(models.Model):
    give_access = models.ForeignKey(GiveAccessToDocumentFolder, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name}: {self.give_access}'



