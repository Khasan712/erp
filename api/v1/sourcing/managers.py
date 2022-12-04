from .enums import SourcingSection
from django.db import models


class SourcingDirectorManager(models.Manager):
    def get_queryset(self):
        return super(SourcingDirectorManager, self).get_queryset().filter(
            general_status=SourcingSection.questionary.value
        )
