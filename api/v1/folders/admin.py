from django.contrib import admin
from .models import (
    FolderOrDocument,
    GiveAccessToDocumentFolder,
    GiveAccessCart
)

admin.site.register(GiveAccessCart)

@admin.register(FolderOrDocument)
class FolderOrDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'created_at', 'updated_at', 'is_trashed', 'is_folder')


@admin.register(GiveAccessToDocumentFolder)
class GiveAccessToDocumentFolderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'creator', 'user', 'folder_or_document', 'editable', 'expiration_date', 'created_at', 'updated_at'
    )



