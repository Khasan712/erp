from django.core.mail import EmailMessage
from api.v1.chat.models import Chat
from api.v1.chat.serializers import ChatSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from api.v1.users.services import make_errors
from rest_framework.views import APIView
from .models import Notification
from api.v1.suppliers.models import (
    Supplier,
    SupplierQuestionary,
)



class ChatGetMenu(generics.ListAPIView):
    queryset = Chat.objects.select_related('sender', 'receiver', 'answer_for')
    serializer_class = ChatSerializer
    
    def get(self, request):
        try:
            """
            partner name
            last message
            last message time
            
            
            chat ID
            unread messages count
            
            """
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occured.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )
    


class ChatListView(generics.ListCreateAPIView):
    queryset = Chat.objects.select_related('sender', 'receiver', 'answer_for')
    serializer_class = ChatSerializer

    def post(self, request):
        try:
            data = request.data
            sender = self.request.user.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                # serializer.object.sender_id = sender
                serializer.save(sender_id = sender)
            else:
                return Response(
                    {
                        "success": False,
                        "message": 'Error occurred.',
                        "error": make_errors(serializer.errors),
                        "data": [],
                    },status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occured.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
                {
                    "success": True,
                    "message": 'User created suucessfully.',
                    "error": [],
                    "data": serializer.data,
                }, status=status.HTTP_201_CREATED
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
        sender_id=total_result.checker.id,
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