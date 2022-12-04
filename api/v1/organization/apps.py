from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.organization'
    label = 'organization'

    def ready(self):
        from . import handlers
