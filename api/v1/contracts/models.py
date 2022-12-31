from datetime import datetime
from django.db import models
from api.v1.organization.models import Organization
from api.v1.services.models import (
    Commodity,
    Service,
    Consultant
)
from api.v1.suppliers.models import Supplier
import datetime
from api.v1.users.models import User
from django.core.exceptions import ValidationError
from .enums import ServiceChoice

structure = (
    ('Stand Alone', 'Stand Alone'),
    ('Master Agreement', 'Master Agreement'),
    ('Sub Agreement', 'Sub Agreement'),
)


class Departement(models.Model):
    name = models.CharField(max_length=75, unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Contract_Type(models.Model):
    name = models.CharField(max_length=50, unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Category(models.Model):
    name = models.CharField(max_length=50)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        categories = Category.objects.filter(organization_id=self.organization.id)
        if self.name.lower() in categories:
            raise ValidationError("Category name has already in database")
        super().save(*args, **kwargs)


class Cost_Center(models.Model):
    num = models.CharField(max_length=7)
    name = models.CharField(max_length=50)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Currency(models.Model):
    name = models.CharField(max_length=10, unique = True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


TERMS = (
    ('Auto Renew', 'Auto Renew'),
    ('Fixed', 'Fixed'),
    ('Perpetual', 'Perpetual')
)


CHOICES = (
    ('DRAFT', 'DRAFT'),
    ('ACTIVE', 'ACTIVE'),
    ('EXPIRED', 'EXPIRED'),
)


class Contract(models.Model):
    # Users
    category_manager = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='categoy_manager')
    contract_owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='contract_owner')
    lawyer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='lawyer')
    project_owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='project_owner')
    # contract dates :
    creation_date = models.DateTimeField(auto_now_add=True)
    effective_date = models.DateField(blank =True, null=True)
    expiration_date = models.DateField(blank =True, null=True)
    duration = models.FloatField(null=True, blank=True)

    # Contract Attributes :
    name = models.CharField(max_length=100, blank=True, null=True)
    contract_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    parent_agreement = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='parrent')
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
    amendment = models.BooleanField(default=False, blank=True, null=True)
    status = models.CharField(choices=CHOICES, max_length=50, default="DRAFT", blank=True, null=True)
    count_changes = models.FloatField(default=0)
    notification = models.FloatField(null=True, blank=True)
    is_send_fixed = models.BooleanField(default=False)

    # Supplier information
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank =True, null=True)
    serviceCommodityConsultant = models.CharField(max_length=10, choices=ServiceChoice.choices(), blank=True, null=True)

    def __str__(self):
        return f'{self.name}: {self.contract_amount}'

    def save(self, *args, **kwargs):
        if self.status == 'ACTIVE' or self.status == 'EXPIRED':
            self.count_changes += 1
        if self.contract_number is None:
            self.contract_number = 'EM-'+str(Contract.objects.count()+1)
        super(Contract, self).save(*args, **kwargs)

    @property
    def get_agreements(self):
        agreements = Contract.objects.select_related('parent_agreement', 'departement', 'category', 'currency',
            'organization', 'create_by', 'supplier').filter(parent_agreement_id=self.id).values(
            'id', 'name', 'contract_number'
        )
        return agreements if agreements else None

    @property
    def get_services(self):
        contract_services = ContractService.objects.select_related('contract', 'service', 'creator').filetr(
                    contract_id=self.id).values('id', 'service__name')
        return contract_services if contract_services else None

    @property
    def get_service_commodity_consultant(self):
        match self.serviceCommodityConsultant:
            case 'service':
                return ContractService.objects.select_related('contract', 'service', 'creator').filter(
                    contract_id=self.id).values('id', 'service__name')
            case 'commodity':
                return ContractCommodity.objects.select_related('contract', 'service', 'creator').filetr(
                    contract_id=self.id).values('id', 'commodity__name')
            case 'consultant':
                return ContractConsultant.objects.select_related('contract', 'service', 'creator').filetr(
                    contract_id=self.id).values('id', 'consultant__f_n', 'consultant__l_n')
            case '':
                return None

    @property
    def get_tasks(self):
        contract_tasks = ConnectContractWithTask.objects.select_related(
            'contract', 'task', 'executor', 'checker',
        ).filter(contract_id=self.id).values('id', 'task__name', 'is_done')
        return contract_tasks if contract_tasks else None

    @property
    def get_documents(self):
        contract_documents = DocumentContact.objects.select_related(
            'contract'
        ).filter(contract_id=self.id).values('id', 'document',)
        return contract_documents if contract_documents else None


class ContractExpirationDayAndStatus(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    from_contract_status = models.CharField(max_length=8, choices=CHOICES)
    to_contract_status = models.CharField(max_length=8, choices=CHOICES)
    old_expiration_day = models.DateField()
    new_expiration_day = models.DateField()

    def __str__(self):
        return f'{self.contract.name}: ID - {self.contract.id}'


class ContractService(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.contract.contract_number} -> {self.service.name}' if self.service and self.contract else f'{self.id}'


class ContractCommodity(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.contract.contract_number} -> {self.commodity.name}' if self.commodity and self.contract else f'{self.id}'


class ContractConsultant(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.contract.contract_number} -> {self.consultant.f_n}' if self.consultant and self.contract else f'{self.id}'


class ContractNotificationDay(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True)
    send_email_day = models.DateField()
    is_send = models.BooleanField(default=False)


class ContractTask(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'


class ConnectContractWithTask(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True)
    task = models.ForeignKey(ContractTask, on_delete=models.SET_NULL, null=True)
    executor = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    checker = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)
    done_at = models.DateTimeField(blank=True, null=True, editable=False)


class DocumentContact(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True)
    document = models.FileField(blank=True, null=True, upload_to='contracts/files/')
    is_signing = models.BooleanField(default=False)



