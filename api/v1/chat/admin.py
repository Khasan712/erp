from django.contrib import admin

# Register your models here.


from api.v1.chat.models import (
    Chat,
    ChatFile,
    Notification
)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'is_read', 'is_active')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'is_read',)
    