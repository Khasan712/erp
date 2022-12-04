from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from config.celery import app
from celery import shared_task
from api.v1.sourcing.models import SourcingRequestEvent, SourcingRequestEventSuppliers
from api.v1.suppliers.models import Supplier
from api.v1.users.models import User


# @app.task()
@shared_task()
def send_message_to_suppliers(current_site, sourcing_event_id):
    sourcing_event = SourcingRequestEvent.objects.get(id=sourcing_event_id)
    relative_link = reverse('event-detail', args=[sourcing_event.id])
    if settings.DEBUG:
        url_path = f'http://{current_site}{relative_link}'
    else:
        url_path = f'http://{current_site}{relative_link}'

    suppliers = SourcingRequestEventSuppliers.objects.select_related('supplier', 'sourcingRequestEvent').filter(
        sourcingRequestEvent_id=sourcing_event.id
    )
    for supplier in suppliers:
        user_supplier = Supplier.objects.select_related('organization', 'create_by', 'supplier', 'parent').get(
            id=supplier.supplier.id
        )
        supplier = User.objects.get(id=user_supplier.supplier.id)
        token = RefreshToken.for_user(supplier).access_token
        body = f"Hi {supplier.first_name}. You have sourcing event. \n{url_path}?token={str(token)}"
        email = EmailMessage(
            body=f"{body}",
            subject=f"Sourcing event.",
            to=[supplier.email],
        )
        email.send()

