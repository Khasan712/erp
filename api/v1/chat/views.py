from django.core.mail import EmailMessage
from .models import Notification
from api.v1.suppliers.models import (
    Supplier,
    SupplierQuestionary,
)


def make_contract_noti(sender_id, receiver_id, contract_id, text):
    Notification.objects.create(
        sender_id=sender_id,
        receiver_id=receiver_id,
        contract_id=contract_id,
        text=text
    )


def send_result_notification(total_result):
    Notification.objects.create(
        # sender_id=total_result.checker.id,
        receiver_id=total_result.supplier.supplier.id,
        text=total_result.questionary_status
    )


def send_alert_supplier_questionary(request, questionary_id):
    suppliers = request.data.get('suppliers')
    questionary = SupplierQuestionary.objects.get(id=questionary_id)
    for supplier in suppliers:
        supplier = Supplier.objects.get(id=supplier.get('id'))
        Notification.objects.create(
            sender_id=request.user.id,
            receiver_id=supplier.supplier.id,
            questionary_id=questionary.id,
            text=f'You have added to the questionary'
        )


def send_email_to_service_creator(email):
    email = EmailMessage(
        body="Working",
        subject="Congratulations.",
        to=[email],
    )
    email.send()


def send_to_supplier_from_contract(email):
    supplier = EmailMessage(
        body="Contract created",
        subject="Something about contract.",
        to=[email],
    )
    supplier.send()
