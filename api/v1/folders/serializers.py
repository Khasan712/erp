from rest_framework import serializers
from .models import (
    FolderOrDocument,
    GiveAccessToDocumentFolder,
    GiveAccessToDocumentFolderUser
)


class PostFolderOrDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderOrDocument
        fields = ('id', 'name', 'document', 'parent')


class ListFolderOrDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderOrDocument
        fields = ('id', 'name', 'document', 'parent')

    def to_representation(self, instance):
        response = super(ListFolderOrDocumentSerializer, self).to_representation(instance)
        if response.get('parent'):
            response['parent'] = {
                'id': instance.parent.id,
                'name': instance.parent.name,
            }
        return response
