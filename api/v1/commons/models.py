from dataclasses import dataclass
from django.db import models
import datetime
# Create your models here.


class AbstractTimeBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(blank=True, null=True)
    deadline_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        super().save(*args, **kwargs)
    
    class Meta:
        abstract = True    