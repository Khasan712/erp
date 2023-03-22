from django.db import models

from api.v1.users.models import User


def upload_location_report(instance, file):
    """
    Uploaded file address | format: (media)/reports/organization/file
    """
    return f'reports/{instance.done_by.organization.name}/{file}'


class Report(models.Model):
    done_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    report_file = models.FileField(upload_to=upload_location_report)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.done_by.first_name} - {self.done_by.organization.name}'
