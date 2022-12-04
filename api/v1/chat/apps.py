from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.chat'
    label = 'chat'
    
    def ready(self):
        import api.v1.chat.signals
