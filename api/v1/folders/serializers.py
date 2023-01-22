from rest_framework import serializers
from .models import (
    FolderOrDocument,
    GiveAccessToDocumentFolder,
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


class PatchAdministratorFolderOrDocumentSerializer(serializers.ModelSerializer):
    """ Only contract administrator can remove folder or document from trash or delete """

    class Meta:
        model = FolderOrDocument
        fields = ('id', 'is_trashed')


class PatchFolderOrDocumentSerializer(serializers.ModelSerializer):
    """ Only contract administrator can remove folder or document from trash or delete """

    class Meta:
        model = FolderOrDocument
        fields = ('id', 'name', 'document', 'is_trashed')


class TrashedFolderOrDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderOrDocument
        fields = ('id', 'name', 'document', 'is_trashed', 'parent')

    def to_representation(self, instance):
        response = super(TrashedFolderOrDocumentSerializer, self).to_representation(instance)
        if response.get('parent'):
            response['parent'] = {
                'id': instance.parent.id,
                'name': instance.parent.name,
            }
        return response


class GedFolderOrDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderOrDocument
        fields = ('id', 'name', 'document')


class GiveAccessToDocumentFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveAccessToDocumentFolder
        fields = ('id', 'user', 'folder_or_document', 'out_side_person', 'editable', 'expiration_date')


class ListGiveAccessToDocumentFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveAccessToDocumentFolder
        fields = ('id', 'user', 'folder_or_document', 'out_side_person', 'editable', 'expiration_date')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response.get('user'):
            response['user'] = {
                'id': instance.user.id,
                'first_name': instance.user.first_name,
                'last_name': instance.user.last_name,
                'email': instance.user.email,
            }
        if instance.folder_or_document.document:
            response['folder_or_document'] = {
                'id': instance.folder_or_document.id,
                'document': instance.folder_or_document.document,
            }
        else:
            response['folder_or_document'] = {
                'id': instance.folder_or_document.id,
                'name': instance.folder_or_document.name,
            }
        return response
