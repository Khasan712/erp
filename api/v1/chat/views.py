from django.core.mail import EmailMessage
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Case, When
from .models import Notification, ChatRoom
from ..commons.pagination import queryset_pagination
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
        all_chat_rooms = ChatRoom.objects.select_related('partner1', 'partner2').filter(
            Q(partner1_id=user.id) | Q(partner2_id=user.id)
        )
        users_data = []
        if not all_chat_rooms:
            return None
        for all_chat_room in all_chat_rooms:
            if all_chat_room.partner1.id == user.id:
                users_data.append({
                    'id': all_chat_room.partner2.id,
                    'first_name': all_chat_room.partner2.first_name,
                    'last_name': all_chat_room.partner2.last_name,
                    'email': all_chat_room.partner2.email,
                    'room_id': all_chat_room.room_id,
                })
            else:
                users_data.append({
                    'id': all_chat_room.partner1.id,
                    'first_name': all_chat_room.partner1.first_name,
                    'last_name': all_chat_room.partner1.last_name,
                    'email': all_chat_room.partner1.email,
                    'room_id': all_chat_room.room_id,
                })
        return users_data

    def get(self, request):
        try:
            params = self.request.query_params
            method = params.get('method')
            if not method or method not in ("connected.users",):
                raise ValueError("Method not given or not found!")
            match method:
                case 'connected.users':
                    data = self.get_connected_users()
                    return Response(queryset_pagination(request, data), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
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
