from django.db import models
from api.v1.services.enums import IncreasePayTerms, PaymentFor, ItemStatuses
from api.v1.users.models import User
from api.v1.organization.models import Organization


class Commodity(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, blank=True, null=True)
    must_increase = models.BooleanField(default=False)
    growthPercentage = models.FloatField(default=0, blank=True, null=True)
    increasePayTerms = models.CharField(max_length=13, choices=IncreasePayTerms.choices())
    frequency = models.FloatField(default=0, blank=True, null=True)
    status = models.CharField(max_length=10, choices=ItemStatuses.choices(), default='expired')
    how_many_times = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'

    @property
    def get_documents(self):
        documents = DocumentService.objects.select_related('commodity', 'service').filter(
            commodity_id=self.pk).values_list('id', 'document')
        return documents

    @property
    def get_price(self):
        commodity_price = ServiceCommodityConsultantPrice.objects.select_related(
            'forService', 'forCommodity', 'forConsultant').filter(forCommodity_id=self.id).last()
        return commodity_price.price if commodity_price else None


class Consultant(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    f_n = models.CharField(max_length=50)
    l_n = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    c_start_d = models.DateField()
    c_end_d = models.DateField()
    paymentFor = models.CharField(max_length=9, choices=PaymentFor.choices())
    must_increase = models.BooleanField(default=False)
    increasePayTerms = models.CharField(max_length=13, choices=IncreasePayTerms.choices())
    how_many_times = models.IntegerField(default=0)
    growthPercentage = models.FloatField(default=0, blank=True, null=True)
    frequency = models.FloatField(default=0, blank=True, null=True)
    status = models.CharField(max_length=10, choices=ItemStatuses.choices(), default='expired')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.f_n} - {self.l_n}'

    @property
    def get_price(self):
        consultant_price = ServiceCommodityConsultantPrice.objects.select_related(
            'forService', 'forCommodity', 'forConsultant').filter(forConsultant_id=self.id).last()
        return consultant_price.price if consultant_price else None


class Service(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, blank=True, null=True)
    frequency = models.FloatField(default=0, blank=True, null=True)
    must_increase = models.BooleanField(default=False)
    increasePayTerms = models.CharField(max_length=13, choices=IncreasePayTerms.choices(), blank=True, null=True)
    how_many_times = models.IntegerField(default=0)
    growthPercentage = models.FloatField(default=0, blank=True, null=True)
    status = models.CharField(max_length=10, choices=ItemStatuses.choices(), default='expired')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.organization.name}: {self.name}'

    @property
    def get_price(self):
        service_price = ServiceCommodityConsultantPrice.objects.select_related(
            'forService', 'forCommodity', 'forConsultant').filter(forService_id=self.id).last()
        return service_price.price if service_price else None

    @property
    def get_commodities(self):
        commodities = ServiceCommodity.objects.select_related('commodity', 'service').filter(
            service_id=self.pk).values('id', 'commodity__name',)
        return commodities

    @property
    def get_documents(self):
        documents = DocumentService.objects.select_related('commodity', 'service').filter(
            service_id=self.pk).values_list('document',)
        return documents


class ServiceCommodity(models.Model):
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    commodity = models.ForeignKey(Commodity, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.service.name}: {self.commodity.name}'


class DocumentService(models.Model):
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    commodity = models.ForeignKey(Commodity, on_delete=models.SET_NULL, null=True)
    document = models.FileField(upload_to='service/files/')

    def __str__(self):
        return self.commodity.name


class ServiceCommodityConsultantPrice(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    forCommodity = models.ForeignKey(Commodity, on_delete=models.SET_NULL, null=True, blank=True)
    forService = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    forConsultant = models.ForeignKey(Consultant, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.organization.name} -> {self.price}'


class ServiceCommodityConsultantPayTermsIncrease(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    forCommodity = models.ForeignKey(Commodity, on_delete=models.SET_NULL, null=True, blank=True)
    forService = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    forConsultant = models.ForeignKey(Consultant, on_delete=models.SET_NULL, null=True, blank=True)

    current_price = models.ForeignKey(ServiceCommodityConsultantPrice, on_delete=models.CASCADE)
    new_price = models.FloatField(default=0)
    growthPercentage = models.FloatField(default=0)
    increaseDay = models.DateField()
    increasePayTerms = models.CharField(max_length=13, choices=IncreasePayTerms.choices())
    how_many_times = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    changed_to_new_price = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_current_price(self):
        return self.current_price.price if self.current_price else None

    # def __str__(self):
    #     return f'{self.organization.name} -> {self.price}' if self.organization and self.price else None
