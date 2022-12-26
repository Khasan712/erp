import datetime

from django.db import models
from django.db.models import Sum, Avg
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError

from api.v1.commons.models import AbstractTimeBase
from api.v1.contracts.enums import ServiceChoice
from api.v1.contracts.models import Currency, Departement
from api.v1.organization.models import Organization
from api.v1.services.models import (
    Commodity,
    Consultant,
    Service,
)
from api.v1.sourcing.enums import (
    SourcingEvent,
    SourcingSection,
    SourcingStatus,
    QuestionaryStatus, SourcingEventSupplierTimeLine
)
from api.v1.users.models import User
from .managers import SourcingDirectorManager
from api.v1.suppliers.models import Supplier
# Create your models here.


class CategoryRequest(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.name}"


class SourcingRequest(AbstractTimeBase):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)
    categoryRequest = models.ForeignKey(CategoryRequest, on_delete=models.SET_NULL, null=True)
    requestor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requestor')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_to')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    estimated_budget = models.FloatField(default=0)
    sourcing_request_name = models.CharField(max_length=255)
    sourcing_number = models.CharField(max_length=50)
    description = models.TextField()
    sourcing_request_status = models.CharField(max_length=11, choices=SourcingStatus.choices(), default='created')
    document = models.FileField(upload_to='SourcingRequest/documents/', blank=True, null=True)
    serviceCommodityConsultant = models.CharField(max_length=10, choices=ServiceChoice.choices(), blank=True, null=True)
    # commodity = models.ForeignKey(Commodity, on_delete=models.SET_NULL, null=True, blank=True)
    # service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    # consultant = models.ForeignKey(Consultant, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def get_documents(self):
        documents = DocumentSourcing.objects.select_related('sourcingRequest', 'sourcingEvent').filter(
            sourcingRequest_id=self.id,
        ).values('sourcingFiles', 'id')
        return documents

    @property
    def sourcing_event(self):
        sourcing_event = SourcingRequestEvent.objects.select_related('sourcing_request', 'creator', 'parent').filter(
            sourcing_request_id=self.pk
        )
        return True if sourcing_event else False

    def save(self, *args, **kwargs):
        if self.sourcing_number == '':
            qty = SourcingRequest.objects.count()
            self.sourcing_number = "EM-"+str(qty+1)
        super().save(*args, **kwargs)

    @property
    def get_assigned_users(self):
        contract_assigned_users = SourcingRequestAssigned.objects.select_related('sourcingRequest', 'assigned').filter(
            sourcingRequest_id=self.id
        ).values('id', 'assigned__first_name', 'assigned__last_name')
        return contract_assigned_users if contract_assigned_users else None


class SourcingRequestAssigned(models.Model):
    sourcingRequest = models.ForeignKey(SourcingRequest, on_delete=models.CASCADE)
    assigned = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sourcingRequest.sourcing_request_name} {self.assigned.first_name}'


class SourcingRequestService(models.Model):
    sourcingRequest = models.ForeignKey(SourcingRequest, on_delete=models.CASCADE)
    sourcingService = models.ForeignKey(Service, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sourcingRequest.sourcing_request_name} - {self.sourcingService.name}"


class SourcingRequestCommodity(models.Model):
    sourcingRequest = models.ForeignKey(SourcingRequest, on_delete=models.CASCADE)
    sourcingCommodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sourcingRequest.sourcing_request_name} - {self.sourcingCommodity.name}"


class SourcingRequestConsultant(models.Model):
    sourcingRequest = models.ForeignKey(SourcingRequest, on_delete=models.CASCADE)
    sourcingConsultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sourcingRequest.sourcing_request_name} - {self.sourcingConsultant.f_n}"


class SourcingRequestEvent(models.Model):
    sourcing_request = models.ForeignKey(SourcingRequest, on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sourcing_event = models.CharField(max_length=10, choices=SourcingEvent.choices(), blank=True, null=True)

    # Section name
    title = models.CharField(max_length=255, blank=True, null=True)
    # Description section
    text = models.TextField(blank=True, null=True)
    # General status (info or questionary or category of questionary or question of category)
    general_status = models.CharField(max_length=14, choices=SourcingSection.choices(), blank=True, null=True)
    # Success weight
    success_weight = models.FloatField(default=0)
    # Weight
    weight = models.FloatField(default=0)
    # question = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    yes_no = models.BooleanField(null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_deadline_at(self):
        return self.sourcing_request.deadline_at

    @property
    def get_questionary_data(self):
        queryset = SourcingRequestEvent.objects.select_related('sourcing_request', 'creator', 'parent')
        categories = []
        for category in queryset.filter(parent_id=self.id, general_status='category'):
            category_questions = []
            for question in queryset.filter(parent_id=category.id, general_status='question'):
                question_obj = {
                    'id': question.id,
                    'text': question.text,
                    'answer': question.answer,
                    'yes_no': question.yes_no,
                    'weight': question.weight,
                }
                category_questions.append(question_obj)
            category_obj = {
                'id': category.id,
                'title': category.title,
                'weight': category.weight,
                'questions': category_questions
            }
            categories.append(category_obj)
        return categories

    @property
    def get_supplier_answer_question(self):
        queryset = SourcingRequestEvent.objects.select_related('sourcing_request', 'creator', 'parent')
        categories = []
        for category in queryset.filter(parent_id=self.id, general_status='category'):
            category_questions = []
            for question in queryset.filter(parent_id=category.id, general_status='question'):
                question_obj = {
                    'id': question.id,
                    'text': question.text,
                    'weight': question.weight,
                }
                category_questions.append(question_obj)
            category_obj = {
                'id': category.id,
                'title': category.title,
                'weight': category.weight,
                'questions': category_questions
            }
            categories.append(category_obj)
        return categories

    def __str__(self):
        return f'{self.general_status}'


class SourcingRequestEventSuppliers(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    sourcingRequestEvent = models.ForeignKey(SourcingRequestEvent, on_delete=models.CASCADE, null=True, related_name='sourcing_request_event')
    created_at = models.DateTimeField(auto_now_add=True)
    supplier_timeline = models.CharField(max_length=11, choices=SourcingEventSupplierTimeLine.choices(), default='not_viewed')

    @property
    def get_total_weight(self):
        total_weight = SupplierAnswer.objects.select_related('supplier', 'question', 'checker').filter(
            supplier_id=self.supplier.id, question__parent__parent__parent_id=self.sourcingRequestEvent.id
        ).aggregate(foo=Coalesce(Sum('weight'), 0.0))['foo']
        return total_weight

    def __str__(self):
        return f'{self.supplier.name} - {self.sourcingRequestEvent.title}'


class DocumentSourcing(models.Model):
    sourcingRequest = models.ForeignKey(SourcingRequest, on_delete=models.SET_NULL, null=True, blank=True)
    sourcingEvent = models.ForeignKey(SourcingRequestEvent, on_delete=models.SET_NULL, null=True, blank=True)
    sourcingFiles = models.FileField(upload_to='sourcing/files/')
    created_at = models.DateTimeField(auto_now_add=True)
    # def save(self, *args, **kwargs):
    #     if not self.sourcingEvent and not self.sourcingRequest:
    #         raise ValidationError("Can not upload file, talk with developers.")
    #     super().save(*args, **kwargs)


class SupplierAnswer(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    question = models.ForeignKey(SourcingRequestEvent, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True)
    yes_no = models.BooleanField(null=True)

    # Chacker
    checker = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='checker')
    weight = models.FloatField(default=0)

    answered_at = models.DateTimeField(auto_now_add=True, editable=False)
    checked_at = models.DateTimeField(editable=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.checker is not None:
            self.checked_at = datetime.datetime.now()
        if self.weight > self.question.weight:
            raise ValidationError("Answer weight is grater then question weight !!!")
        super().save(*args, **kwargs)


class SupplierResult(models.Model):
    questionary = models.ForeignKey(SourcingRequestEvent, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    checker = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    total_weight = models.FloatField(default=0)
    questionary_status = models.CharField(max_length=15, choices=QuestionaryStatus.choices())
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.total_weight} > {self.questionary_status}"


class SourcingComments(models.Model):
    sourcingRequest = models.ForeignKey(SourcingRequest, on_delete=models.SET_NULL, null=True)
    sourcingRequestEvent = models.ForeignKey(SourcingRequestEvent, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
