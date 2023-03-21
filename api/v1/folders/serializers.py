from rest_framework import serializers
from .models import (
    FolderOrDocument,
    GiveAccessToDocumentFolder,
    GiveAccessCart
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
        fields = ('id', 'give_access_cart', 'folder_or_document')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['give_access_cart'] = {

        }


class ShareLinkGiveAccessToDocumentFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveAccessToDocumentFolder
        fields = ('id', 'folder_or_document', 'out_side_person', 'editable', 'expiration_date', 'access_code')


class UpdateGiveAccessToDocumentFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveAccessToDocumentFolder
        fields = ('id', 'editable', 'expiration_date')


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
        if not instance.folder_or_document.document:
            response['folder_or_document'] = {
                'id': instance.folder_or_document.id,
                'name': instance.folder_or_document.name,
            }
        if instance.folder_or_document.document:
            response['folder_or_document'] = {
                'id': instance.folder_or_document.id,
                'document': f'/media/{instance.folder_or_document.document.name}',
            }
        return response


class UsersGiveAccessToDocumentFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveAccessToDocumentFolder
        fields = ('id', 'user')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if res.get('user'):
            res['user'] = {
                'id': instance.user.id,
                'first_name': instance.user.first_name,
                'last_name': instance.user.last_name,
                'email': instance.user.email,
                'role': instance.user.role,
                'is_outside': False,
            }
        else:
            res['user'] = {
                'email': instance.out_side_person,
                'is_outside': True,
            }
        return res


class ListOutsideGiveAccessToDocumentFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveAccessToDocumentFolder
        fields = ('id', 'user', 'folder_or_document', 'editable', 'expiration_date')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response.get('user'):
            response['user'] = {
                'id': instance.user.id,
                'first_name': instance.user.first_name,
                'last_name': instance.user.last_name,
                'email': instance.user.email,
            }
        if not instance.folder_or_document.document:
            response['folder_or_document'] = {
                'id': instance.folder_or_document.id,
                'name': instance.folder_or_document.name,
            }
        if instance.folder_or_document.document:
            response['folder_or_document'] = {
                'id': instance.folder_or_document.id,
                'document': f'/media/{instance.folder_or_document.document.name}',
            }
        return response


class SharedLinkListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveAccessToDocumentFolder
        fields = ('id', 'user', 'folder_or_document', 'editable', 'expiration_date', 'access_code')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response.get('user'):
            response['user'] = {
                'id': instance.user.id,
                'first_name': instance.user.first_name,
                'last_name': instance.user.last_name,
                'email': instance.user.email,
            }
        if not instance.folder_or_document.document:
            response['folder_or_document'] = {
                'id': instance.folder_or_document.id,
                'name': instance.folder_or_document.name,
            }
        if instance.folder_or_document.document:
            response['folder_or_document'] = {
                'id': instance.folder_or_document.id,
                'document': f'/media/{instance.folder_or_document.document.name}',
            }
        return response


class UpdateOutsideInvitesDocumentFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderOrDocument
        fields = ('id', 'name', 'document')


class GetSharedLinkInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveAccessToDocumentFolder
        fields = ('id', 'folder_or_document')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if not instance.folder_or_document.document:
            res['folder_or_document'] = {
                'id': instance.folder_or_document_id,
                'name': instance.folder_or_document.name,
            }
        else:
            res['folder_or_document'] = {
                'id': instance.folder_or_document_id,
                'document': f'/media/{instance.folder_or_document.document.name}'
            }
        return res


class GetSharedLinkDocumentOrFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderOrDocument
        fields = ('id', 'name', 'document')


class GiveAccessCartSharedSerializer(serializers.ModelSerializer):

    editable = serializers.SerializerMethodField()
    expiration_date = serializers.SerializerMethodField()

    class Meta:
        model = GiveAccessCart
<<<<<<< HEAD
        fields = ('id', 'creator', 'out_side_person', 'created_at')


class GiveAccessCartSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    class Meta:
        model = GiveAccessCart
        fields = ('id', 'creator', 'user', 'editable', 'expiration_date', 'created_at')

    def get_user(self, instance):
        if instance.internal:
            return {
                'id': instance.internal.id,
                'first_name': instance.internal.first_name,
                'last_name': instance.internal.last_name,
                'email': instance.internal.email,
            }
        else:
            return instance.external
=======
        fields = ('id', 'out_side_person', 'created_at', 'editable', 'expiration_date')

    def get_editable(self, instance):
        return GiveAccessToDocumentFolder.objects.select_related(
            'organization', 'creator', 'user', 'folder_or_document', 'shared_link_cart'
        ).filter(shared_link_cart_id=instance.id).first().editable

    def get_expiration_date(self, instance):
        return GiveAccessToDocumentFolder.objects.select_related(
            'organization', 'creator', 'user', 'folder_or_document', 'shared_link_cart'
        ).filter(shared_link_cart_id=instance.id).first().expiration_date


>>>>>>> 5f45d52 (External user open folder bug fixed)
