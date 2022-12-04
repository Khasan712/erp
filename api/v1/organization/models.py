from django.db import models
# from users.models import (
#     SourcingDirector,
# )


class Organization(models.Model):
    name = models.CharField(max_length=75, unique=True)
    address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=12)
    city = models.CharField(max_length=30)
    country = models.CharField(max_length=50)
    # sourcing_director = models.ForeignKey(SourcingDirector, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return self.name
