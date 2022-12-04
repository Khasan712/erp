from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import (
    Service,
    Commodity,
    Consultant,
    ServiceCommodityConsultantPayTermsIncrease, ServiceCommodityConsultantPrice,
)


# @receiver(post_save, sender=Service)
# def service_terms(sender, instance, created, **kwargs):
#     if created:
#         service_price = ServiceCommodityConsultantPrice.objects.select_related(
#             'organization', 'forCommodity', 'forService', 'forConsultant').filter(forService_id=instance.id).last()
#         service_term = ServiceCommodityConsultantPayTermsIncrease(
#             organization_id=instance.organization.id,
#             forService_id=instance.id,
#             increaseTerms=instance.increasePayTerms,
#             growthPercentage=instance.growthPercentage
#         )
#         service_term.increaseDay = get_increase_date(instance.increasePayTerms)
#         service_term.price = (service_price.price * instance.growthPercentage) / 100
#         service_term.save()

