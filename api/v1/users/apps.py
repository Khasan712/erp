from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.users'
    label = 'users'
    
    def ready(self):
        # Makes sure all signal handlers are connected
        from . import handlers  # noqa
