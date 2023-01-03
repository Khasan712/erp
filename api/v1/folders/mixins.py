from django.db import models
from api.v1.organization.models import Organization
from api.v1.users.models import User


class DocumentFolderMixin(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(blank=True, null=True, editable=False)
    is_trashed = models.BooleanField(default=False)

    class Meta:
        abstract = True
