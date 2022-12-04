from django.contrib import admin

from .models import (
    Service,
    Commodity,
    Consultant,
    ServiceCommodityConsultantPrice,
    ServiceCommodityConsultantPayTermsIncrease
)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organization', 'creator', 'name', 'get_price', 'frequency', 'must_increase', 'increasePayTerms',
        'growthPercentage')


@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organization', 'creator', 'name', 'get_price', 'frequency', 'must_increase', 'increasePayTerms',
        'growthPercentage')


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organization', 'creator', 'f_n', 'l_n', 'email', 'get_price', 'frequency', 'must_increase',
        'increasePayTerms', 'growthPercentage')


@admin.register(ServiceCommodityConsultantPrice)
class ServiceCommodityConsultantPriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'forCommodity', 'forService', 'forConsultant', 'price')
    list_filter = ('organization', 'forCommodity', 'forService', 'forConsultant')


@admin.register(ServiceCommodityConsultantPayTermsIncrease)
class ServiceCommodityConsultantPayTermsIncreaseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organization', 'forCommodity', 'forService', 'forConsultant', 'increasePayTerms',  'get_current_price',
        'new_price', 'growthPercentage', 'increaseDay')

