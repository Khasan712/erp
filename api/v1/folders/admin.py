from django.contrib import admin
from .models import (
    FolderOrDocument,
    GiveAccessToDocumentFolder,
)


@admin.register(FolderOrDocument)
class FolderOrDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'created_at', 'updated_at', 'is_trashed', 'is_folder')


@admin.register(GiveAccessToDocumentFolder)
class GiveAccessToDocumentFolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'folder_or_document', 'editable', 'expiration_date', 'created_at', 'updated_at')



