from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db import transaction
from .models import (
    SourcingRequestEventSuppliers,
    SupplierAnswer,
    SourcingRequestEvent
)


@receiver(post_save, sender=SourcingRequestEvent)
def service_terms(sender, instance, created, **kwargs):
    if created and instance.general_status == 'question':
        request_event = SourcingRequestEvent.objects.select_related('sourcing_request', 'creator', 'parent').filter(
            id=instance.parent.parent.parent.id
        ).first()
        request_event_suppliers = SourcingRequestEventSuppliers.objects.select_related(
            'supplier', 'sourcingRequestEvent').filter(sourcingRequestEvent_id=request_event.id)
        with transaction.atomic():
            for supplier in request_event_suppliers:
                supplier_answer_question = SupplierAnswer(
                    supplier_id=supplier.supplier.id,
                    question_id=instance.id
                )
                supplier_answer_question.save()
