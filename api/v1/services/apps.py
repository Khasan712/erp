from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.services'
    label = 'services'

    def ready(self):
        from . import (
            handlers,
            signals
        )
