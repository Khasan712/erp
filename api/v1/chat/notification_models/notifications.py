from django.db import models
from api.v1.contracts.models import Contract
from api.v1.users.models import User


class ContractNotification(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.receiver.email} - {self.contract.contract_number}'
