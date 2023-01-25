from django.contrib import admin

# Register your models here.


from api.v1.chat.models import (
    Chat,
    ChatFile,
    Notification
)

from api.v1.chat.notification_models.notifications import (
    FolderOrDocumentAccessNotification,
)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'is_read', 'is_active')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'is_read',)


@admin.register(FolderOrDocumentAccessNotification)
class FolderOrDocumentAccessNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'is_read',)
    