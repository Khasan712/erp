from django.core.mail import EmailMessage
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Notification
from ..commons.views import exception_response
from api.v1.suppliers.models import (
    Supplier,
    SupplierQuestionary,
)
from ..users.models import User


class ChatApi(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_connected_users(self):
        user = self.request.user
        connected_users = User.objects.select_related('organizations').filter(
            Q(chat_partner1__partner1_id=user.id) | Q(chat_partner1__partner2_id=user.id)
        )
        return connected_users.values('id', 'email', 'first_name', 'last_name')

    def get(self, request):
        try:
            user = self.request.user
            request_data = self.request.data
            method = request_data.get('method')
            data = None
            match method:
                case 'connected.users':
                    data = self.get_connected_users()
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                'success': True,
                'data': data
            }
        )


def make_contract_noti(sender_id, receiver_id, contract_id, text):
    Notification.objects.create(
        sender_id=sender_id,
        receiver_id=receiver_id,
        contract_id=contract_id,
        text=text
    )


def send_result_notification(total_result, user_id):
    Notification.objects.create(
        sender_id=user_id,
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
