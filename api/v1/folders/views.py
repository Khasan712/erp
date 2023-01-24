from django.core.exceptions import ValidationError
from django.db import transaction
import re
from django.shortcuts import render
from rest_framework import generics, views, status, permissions
from django.db.models import Q
from rest_framework.response import Response
from .serializers import (
    PostFolderOrDocumentSerializer, ListFolderOrDocumentSerializer, PatchFolderOrDocumentSerializer,
    PatchAdministratorFolderOrDocumentSerializer, TrashedFolderOrDocumentSerializer, GedFolderOrDocumentSerializer,
    GiveAccessToDocumentFolderSerializer, ListGiveAccessToDocumentFolderSerializer,
    UpdateGiveAccessToDocumentFolderSerializer,
)
from api.v1.users.models import User
from .models import (
    FolderOrDocument, GiveAccessToDocumentFolder,
)
from ..commons.pagination import make_pagination
from ..commons.views import (
    exception_response, not_serializer_is_valid, serializer_valid_response, object_deleted_response,
    serializer_update_valid_response, object_not_found_response, get_error_response,
)
from ..users.permissions import IsSourcingDirector, IsContractAdministrator
from ..users.serializers import UserUpdateSerializer, FolderDocumentUsersSerializer
from ..users.services import make_errors


class PostListFolderOrDocumentApi(views.APIView):
    """ Create document or folder """
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent')

    def get_filter(self):
        user = self.request.user
        queryset = self.get_queryset().filter(
            creator_id=user.id, is_trashed=False, organization_id=user.organization.id
        )
        params = self.request.query_params
        q = params.get('q')
        parent_id = params.get('parent')
        if not parent_id:
            queryset = queryset.filter(parent__isnull=True)
        elif parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(document_folder__document__icontains=q))
        return queryset

    def post(self, request):
        try:
            user = self.request.user
            serializer = PostFolderOrDocumentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer))
            serializer.save(creator_id=user.id, organization_id=user.organization.id)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_valid_response(serializer), status=status.HTTP_201_CREATED)

    def get(self, request):
        try:
            filtered_queryset = self.get_filter()
            serializer = ListFolderOrDocumentSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(make_pagination(request, serializer, filtered_queryset), status=status.HTTP_200_OK)


class PatchDeleteFolderOrDocumentApi(views.APIView):
    """ Update document or folder """
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent')

    def get_object(self, id):
        try:
            item = self.get_queryset().get(id=id)
        except Exception as e:
            raise ValidationError('Object not found.')
        else:
            return item

    def patch(self, request, id):
        try:
            serializer = PatchFolderOrDocumentSerializer(self.get_object(id), data=self.request.data, partial=True)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_valid_response(serializer), status=status.HTTP_200_OK)

    def get(self, request, id):
        try:
            serializer = GedFolderOrDocumentSerializer(self.get_object(id), data=self.request.data, partial=True)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_valid_response(serializer), status=status.HTTP_200_OK)


class MoveToTrashDocumentFolderApi(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent')

    def get_object(self, id):
        try:
            item = self.get_queryset().get(id=id)
        except Exception as e:
            raise ValidationError('Object not found.')
        else:
            return item

    def move_to_trash(self, items: list):
        with transaction.atomic():
            for item in items:
                obj = self.get_object(item)
                if obj.creator.id != self.request.user.id:
                    raise ValidationError('Do not hack!')
                obj.is_trashed = True
                obj.save()

    def delete(self, request):
        try:
            items = self.request.data
            self.move_to_trash(items)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(object_deleted_response(), status=status.HTTP_204_NO_CONTENT)


class ListUsersDocumentFolderAPI(views.APIView):
    """ This API for Sourcing director to see all employee documents and folders """
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector)

    def get_queryset(self):
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent')

    def get_filter(self):
        params = self.request.query_params
        user = self.request.user
        selected_user = params.get('user')
        if not selected_user:
            raise ValidationError('Select user')
        queryset = self.get_queryset().filter(
            is_trashed=False, organization_id=user.organization.id, creator_id=selected_user
        )
        q = params.get('q')
        parent_id = params.get('parent')
        if not parent_id:
            queryset = queryset.filter(parent__isnull=True)
        elif parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(document_folder__document__icontains=q))
        return queryset

    def get(self, request):
        try:
            filtered_queryset = self.get_filter()
            serializer = ListFolderOrDocumentSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(make_pagination(request, serializer, filtered_queryset), status=status.HTTP_200_OK)


class RemoveTrashOrDeleteFolderOrDocumentApi(views.APIView):
    """ This api for remove folder or document from trash or delete """

    permission_classes = (permissions.IsAuthenticated, IsContractAdministrator)

    def get_queryset(self):
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent')

    def get_object(self, id):
        try:
            item = self.get_queryset().get(id=id)
        except Exception as e:
            raise ValidationError('Object not found.')
        else:
            return item

    def delete_stuffs(self, items: list):
        with transaction.atomic():
            for item in items:
                obj = self.get_object(item)
                obj.delete()

    def remove_stuffs(self, items: list):
        with transaction.atomic():
            for item in items:
                obj = self.get_object(item)
                obj.is_trashed = False
                obj.save()

    def patch(self, request):
        """ Remove items from trashes """
        try:
            items = self.request.data
            self.remove_stuffs(items)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                'success': True,
                'message': "Successfully removed from trash",
                'error': [],
                'data': []
            }
        )

    def delete(self, request):
        """ Delete items """
        try:
            items = self.request.data
            self.delete_stuffs(items)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                'success': True,
                'message': "Successfully deleted.",
                'error': [],
                'data': []
            }
        )


class TrashedDocumentFolderApi(views.APIView):
    """ It is api only for contract administrator, It will present trashed documents and folders. """
    permission_classes = (permissions.IsAuthenticated, IsContractAdministrator)

    def get_queryset(self):
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent')

    def get_filter(self):
        user = self.request.user
        queryset = self.get_queryset().filter(
            is_trashed=True, organization_id=user.organization.id
        )
        params = self.request.query_params
        q = params.get('q')
        parent_id = params.get('parent')
        if not parent_id:
            queryset = queryset.filter(parent__isnull=True)
        elif parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(document_folder__document__icontains=q))
        return queryset

    def get(self, request):
        try:
            filtered_queryset = self.get_filter()
            serializer = TrashedFolderOrDocumentSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(make_pagination(request, serializer, filtered_queryset), status=status.HTTP_200_OK)


class GiveAccessToDocumentFolderApi(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = GiveAccessToDocumentFolder.objects.select_related(
            'organization', 'creator', 'user', 'folder_or_document'
        ).filter(organization_id=self.request.user.organization.id)
        return queryset

    def get_object(self):
        user = self.request.user
        params = self.request.query_params
        invite = params.get('invite')
        try:
            invite = int(invite)
        except ValueError:
            return 'Send invite=`ID` in the params.'
        return self.get_queryset().filter(id=invite, creator_id=user.id).first()

    def get_filtered_queryset(self):
        user = self.request.user
        params = self.request.query_params
        invited_user = params.get('user')
        if invited_user:
            try:
                invited_user = int(invited_user)
            except ValueError:
                return 'Send only user id.'
            return self.get_queryset().filter(creator_id=user.id, user_id=invited_user)
        return 'Send user=`ID` in the params.'

    def isValid(self, email):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def give_access_for_user(
            self, creator, users: list, folders_or_documents: list, editable: bool, expiration_date: str,
    ):
        with transaction.atomic():
            documents_and_folders = FolderOrDocument.objects.select_related('organization', 'creator', 'parent')
            for folder_or_document in folders_or_documents:
                folder_document = documents_and_folders.filter(id=folder_or_document).first()
                if not folder_document:
                    return f'{folder_or_document} is not valid document or folder.'
                with transaction.atomic():
                    for user in users:
                        if isinstance(user, int):
                            user_obj = User.objects.filter(id=user).first()
                            if not user_obj:
                                return f'{user} is not valid user id.'
                            data = {
                                'user': user,
                                'folder_or_document': folder_or_document,
                                'editable': editable,
                                'expiration_date': expiration_date,
                            }
                            serializer = GiveAccessToDocumentFolderSerializer(data=data)
                            if not serializer.is_valid():
                                return make_errors(serializer.errors)
                            serializer.save(creator_id=creator.id, organization_id=creator.organization.id)
                        if isinstance(user, str):
                            out_side_person = self.isValid(user)
                            if not out_side_person:
                                return f"{user} is not valid email"
                            data = {
                                'out_side_person': user,
                                'folder_or_document': folder_or_document,
                                'editable': editable,
                                'expiration_date': expiration_date,
                            }
                            serializer = GiveAccessToDocumentFolderSerializer(data=data)
                            if not serializer.is_valid():
                                return make_errors(serializer.errors)
                            serializer.save(creator_id=creator.id, organization_id=creator.organization.id)
                        # else:
                        #     return f'user {user} is not valid type. id - int or email - str.'

        return True

    def post(self, request):
        try:
            creator = self.request.user
            data = self.request.data
            access_users = data.get('users')
            folders_or_documents = data.get('folder_or_document')
            editable = data.get('editable')
            expiration_date = data.get('expiration_date')
            give_access = self.give_access_for_user(
                creator, access_users, folders_or_documents, editable, expiration_date
            )
            if give_access != True:
                return Response(
                    {
                        'success': False,
                        'message': 'Error occurred.',
                        'error': give_access,
                        'data': []
                    }
                )
            if access_users and folders_or_documents:
                pass
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {
                    'success': True,
                    'message': 'Data created successfully.',
                    'error': [],
                    'data': []
                }, status=status.HTTP_201_CREATED
            )

    def get(self, request):
        try:
            invited_user = self.get_filtered_queryset()
            if isinstance(invited_user, str):
                return Response(get_error_response(invited_user))
            serializer = ListGiveAccessToDocumentFolderSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(make_pagination(request, serializer, invited_user))

    def patch(self, request):
        try:
            obj = self.get_object()
            if not obj:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            if isinstance(obj, str):
                return Response(get_error_response(obj), status=status.HTTP_400_BAD_REQUEST)
            serializer = UpdateGiveAccessToDocumentFolderSerializer(obj, data=self.request.data, partial=True)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer), status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_update_valid_response(serializer), status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            obj = self.get_object()
            if not obj:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            if isinstance(obj, str):
                return Response(get_error_response(obj), status=status.HTTP_400_BAD_REQUEST)
            obj.delete()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(object_deleted_response(), status=status.HTTP_204_NO_CONTENT)


class OutsideInvitesApi(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = GiveAccessToDocumentFolder.objects.select_related(
            'organization', 'creator', 'user', 'folder_or_document'
        ).filter(organization_id=self.request.user.organization.id)
        return queryset

    def get_filtered_queryset(self):
        user = self.request.user
        params = self.request.query_params
        outside_user_invited = params.get('user')
        if outside_user_invited:
            try:
                outside_user_invited = int(outside_user_invited)
            except ValueError:
                return 'Send only user id.'
            return self.get_queryset().filter(creator_id=outside_user_invited, user_id=user.id)
        return 'Send user=`ID` in the params.'

    def get(self, request):
        try:
            outside_invites = self.get_filtered_queryset()
            if isinstance(outside_invites, str):
                return Response(get_error_response(outside_invites))
            serializer = ListGiveAccessToDocumentFolderSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(make_pagination(request, serializer, outside_invites))


class FolderDocumentUsersApi(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = User.objects.select_related('organization').filter(organization_id=self.request.user.organization.id)
        return queryset

    def get_users(self):
        user = self.request.user
        params = self.request.query_params
        users = params.get('users')
        if users:
            match users:
                case 'general':
                    if user.role != 'sourcing_director':
                        return "You must be the sourcing director of this website"
                    return self.get_queryset().filter(folder_creator__isnull=False).distinct()
                case 'my_invites':
                    return self.get_queryset().filter(access_user__creator_id=user.id).distinct()
                case 'outside_invites':
                    return self.get_queryset().filter(
                        access_creator__user_id=user.id, access_creator__isnull=False
                    ).distinct()
        else:
            return 'send users=general `or` my_invites `or` outside_invites, in the params.'

    def get(self, request):
        try:
            users = self.get_users()
            if isinstance(users, str):
                return Response(get_error_response(users), status=status.HTTP_400_BAD_REQUEST)
            serializer = FolderDocumentUsersSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(make_pagination(request, serializer, users))

