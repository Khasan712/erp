from rest_framework import serializers
from api.v1.chat.models import Chat


class ChatSerializer(serializers.ModelSerializer):
    # receiver = serializers.For(required=True)
    class Meta:
        model = Chat
        fields = ('id', 'receiver', 'message', 'answer_for')
