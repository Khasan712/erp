from django.db import models

from api.v1.organization.models import Organization
from api.v1.services.models import Commodity, Consultant, Service
from api.v1.suppliers.models import Supplier
from .enums import ServiceChoice
from .models import (
    Contract,
    Departement, structure, Currency, TERMS, CHOICES, Category
)
from api.v1.users.models import User


class HistoryContract(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='contract_history')

    category_manager = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='history_contract_categoy_manager')
    contract_owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='history_contract_contract_owner')
    lawyer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='history_contract_lawyer')
    project_owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='history_contract_project_owner')
    # contract dates :
    creation_date = models.DateTimeField(auto_now_add=True)
    effective_date = models.DateField(blank =True, null=True)
    expiration_date = models.DateField(blank =True, null=True)
    duration = models.FloatField(null=True, blank=True)

    # Contract Attributes :
    name = models.CharField(max_length=100, blank=True, null=True)
    contract_number = models.CharField(max_length=15, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    parent_agreement = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='history_contract_parrent')
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, blank =True, null=True)
    contract_structure = models.CharField(max_length=50, choices=structure, blank =True, null=True)
    contract_amount = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank =True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, blank =True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank =True, null=True)
    create_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    # contract terms
    terms = models.CharField(max_length=50, choices=TERMS, blank=True, null=True)
    contract_notice = models.FloatField(null=True, blank=True)
    contract_amendment = models.BooleanField(default=False, blank=True, null=True)
    status = models.CharField(choices=CHOICES, max_length=50, default="DRAFT", blank=True, null=True)
    count_changes = models.FloatField(default=0)
    notification = models.FloatField(null=True, blank=True)
    is_send_fixed = models.BooleanField(default=False)

    # Supplier information
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank =True, null=True)
    serviceCommodityConsultant = models.CharField(max_length=10, choices=ServiceChoice.choices(), blank=True, null=True)



