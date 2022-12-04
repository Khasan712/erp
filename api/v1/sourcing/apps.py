from django.apps import AppConfig


class SourcingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.sourcing'
    label = 'sourcing'

    def ready(self):
        try:
            from . import (
                handlers,
                signals
            )
        except ImportError:
            pass
