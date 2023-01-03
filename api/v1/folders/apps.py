from django.apps import AppConfig


class FoldersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.folders'
    label = 'folders'

    def ready(self):
        try:
            from . import (
                signals,
            )
        except ImportError:
            pass
