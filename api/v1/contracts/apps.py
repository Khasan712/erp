from django.apps import AppConfig


class ContractsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.contracts'
    label = 'contracts'

    def ready(self):
        from . import (
            handlers,
            signals
        )
