from rest_framework import serializers
from .models import ChatRoom, Chat


class GetRoomChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('id', 'user', 'message', 'answer_for', 'is_read')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if res.get(instance.answer_for):
            res['answer_for'] = {
                'id': instance.answer_for.id,
                "message": instance.answer_for.message
            }
        return res
