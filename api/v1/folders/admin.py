from django.contrib import admin
from .models import (
    FolderOrDocument,
    GiveAccessToDocumentFolder,
    GiveAccessCart
)


@admin.register(FolderOrDocument)
class FolderOrDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'created_at', 'updated_at', 'is_trashed', 'is_folder')


@admin.register(GiveAccessToDocumentFolder)
class GiveAccessToDocumentFolderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organization', 'creator', 'user', 'folder_or_document', 'shared_link_cart', 'out_side_person', 'editable', 'expiration_date'
    )


@admin.register(GiveAccessCart)
class GiveAccessCartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organization', 'creator', 'out_side_person', 'access_code', 'created_at'
    )


