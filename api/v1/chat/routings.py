from django.urls import path

# from api.v1.chat.consumers import ChatConsumer


from api.v1.chat.consumers import TextRoomConsumer


websocket_urlpatterns = [
    path('chat/<str:chat_room>/', TextRoomConsumer.as_asgi()),
]
