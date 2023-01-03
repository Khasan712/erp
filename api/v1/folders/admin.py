from django.contrib import admin
from .models import (
    Folder,
    Document,
    GiveAccessToDocumentFolder,
    GiveAccessToDocumentFolderUser
)
# Register your models here.


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'created_at', 'updated_at', 'is_trashed')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'organization', 'created_at', 'updated_at', 'is_trashed')


@admin.register(GiveAccessToDocumentFolder)
class GiveAccessToDocumentFolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'folder', 'editable', 'expiration_date', 'created_at', 'updated_at')


@admin.register(GiveAccessToDocumentFolderUser)
class GiveAccessToDocumentFolderUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'give_access', 'user')

