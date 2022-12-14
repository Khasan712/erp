from django.apps import AppConfig


class SuppliersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.suppliers'
    label = 'suppliers'

    def ready(self):
        try:
            from . import (
                handlers,
                signals
            )
        except ImportError:
            pass
