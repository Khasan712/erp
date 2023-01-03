from rest_framework import serializers
from .models import (
    Folder,
    Document,
    GiveAccessToDocumentFolder,
    GiveAccessToDocumentFolderUser
)


class PostFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ('id', 'name')


class ListFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ('id', 'name')



