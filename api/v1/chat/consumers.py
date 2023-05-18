from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from api.v1.chat.models import ChatRoom, Chat
from api.v1.users.models import User
from asgiref.sync import async_to_sync
import json


class TextRoomConsumer(WebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_room = None
        self.room_group_name = None
        # self.room = None
        
    def connect(self):
        self.chat_room = self.scope['url_route']['kwargs']['chat_room']
        self.room_group_name = self.chat_room
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # def receive(self, text_data):
    #     # Receive message from WebSocket
    #     text_data_json = json.loads(text_data)
    #     text = text_data_json['text']
    #     sender = text_data_json['sender']
    #     # Send message to room group
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message': text,
    #             'sender': sender
    #         }
    #     )

    # def chat_message(self, event):
    #     # Receive message from room group
    #     text = event['message']
    #     sender = event['sender']
    #     # Send message to WebSocket
    #     self.send(text_data=json.dumps({
    #         'text': text,
    #         'sender': sender
    #     }))