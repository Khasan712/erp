from django.db import models
from api.v1.organization.models import Organization
from api.v1.users.models import User
from api.v1.sourcing.enums import (
    SourcingSection,
    QuestionaryStatus
)
import datetime
from .enums import SupplierStatusChoice
from django.core.exceptions import ValidationError


class Supplier(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    create_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    supplier = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_user', blank=True, null=True)
    parent_supplier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_supplier', blank=True, null=True)
    name = models.CharField(max_length=75, unique=True)
    account = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=70)
    supplier_status = models.CharField(max_length=8, choices=SupplierStatusChoice.choices(), default='active')
    billing_address = models.CharField(max_length=255, blank=True, null=True)
    same_billing_address = models.BooleanField(default=False)
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    transit_number = models.CharField(max_length=15, blank=True, null=True)
    institution_number = models.CharField(max_length=10, blank=True, null=True)
    bank_account = models.CharField(max_length=30, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='parents')

    # def save(self, *args, **kwargs):
    #     # if self.account == '':
    #     #     suppliers_qty = Supplier.objects.select_related('organization', 'create_by', 'supplier', 'parent').count()
    #     #     self.account = suppliers_qty + 1
    #     # if self.parent is not None and self.same_billing_address:
    #     #     self.billing_address = self.parent.billing_address
    #     # if self.supplier is not None and self.supplier.role != 'supplier':
    #     #     raise ValidationError('Only suppliers can assign.')
    #     super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def get_children(self):
        children = Supplier.objects.select_related('organization', 'create_by', 'supplier', 'parent').filter(
            parent_id=self.id).values('id', 'name', 'account')
        return children


class SupplierQuestionary(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    # Description section
    text = models.TextField(blank=True, null=True)
    # General status (info or questionary or category of questionary or question of category)
    general_status = models.CharField(max_length=14, choices=SourcingSection.choices(), blank=True, null=True)
    # Weight
    weight = models.FloatField(default=0)
    # Answer & Question
    question = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class QuestionarySuppliers(models.Model):
    questionary = models.ForeignKey(SupplierQuestionary, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class QuestionaryDocument(models.Model):
    questionary = models.ForeignKey(SupplierQuestionary, on_delete=models.SET_NULL, null=True, blank=True)
    sourcingFiles = models.FileField(upload_to='supplier/questionary/files/')


class SupplierQuestionaryAnswer(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    checker = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey(SupplierQuestionary, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True)
    yes_no = models.BooleanField(default=False, blank=True, null=True)
    # Checker
    is_true = models.BooleanField(default=False)
    checker_message = models.TextField(blank=True, null=True)
    weight = models.FloatField(default=0)

    answered_at = models.DateTimeField(auto_now_add=True, editable=False)
    checked_at = models.DateTimeField(editable=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.checker:
            self.checked_at = datetime.datetime.now()
        # if self.weight > self.question.weight:
        #     raise ValidationError("Answer weight is grater then question weight !!!")
        super().save(*args, **kwargs)


class SupplierQuestionaryResult(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    checker = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    questionary = models.ForeignKey(SupplierQuestionary, on_delete=models.SET_NULL, null=True)
    total_weight = models.FloatField(default=0)
    questionary_status = models.CharField(max_length=15, choices=QuestionaryStatus.choices())
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.total_weight} > {self.questionary_status}"


class SupplierComments(models.Model):
    questionary = models.ForeignKey(SupplierQuestionary, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
