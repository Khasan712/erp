from itertools import chain
from django.conf import settings
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
    UpdateGiveAccessToDocumentFolderSerializer, UsersGiveAccessToDocumentFolderSerializer,
    ListOutsideGiveAccessToDocumentFolderSerializer, UpdateOutsideInvitesDocumentFolderSerializer,
    GetSharedLinkInviteSerializer, GetSharedLinkDocumentOrFolderSerializer,
    ShareLinkGiveAccessToDocumentFolderSerializer, GiveAccessCartSharedSerializer, SharedLinkListSerializer,
)
from api.v1.users.models import User
from .models import (
    FolderOrDocument, GiveAccessToDocumentFolder, GiveAccessCart,
)
from ..chat.tasks import folder_or_document_access_notification, send_shared_link_email
from ..commons.pagination import make_pagination
from ..commons.views import (
    exception_response, not_serializer_is_valid, serializer_valid_response, object_deleted_response,
    serializer_update_valid_response, object_not_found_response, get_error_response, get_valid_response,
)
from ..users.permissions import IsSourcingDirector, IsContractAdministrator
from ..users.serializers import UserUpdateSerializer, FolderDocumentUsersSerializer
from ..users.services import make_errors
from ..users.utils import Utils


class PostListFolderOrDocumentApi(views.APIView):
    """ Create document or folder and get list"""
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
    """ Update document or folder by id"""
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent').filter(
            creator_id=self.request.user.id, organization_id=self.request.user.organization.id, is_trashed=False
        )

    def get_object(self, pk):
        item = self.get_queryset().filter(id=pk).first()
        if not item:
            return None
        return item

    def patch(self, request, pk):
        try:
            item_obj = self.get_object(pk)
            if not item_obj:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            serializer = PatchFolderOrDocumentSerializer(item_obj, data=self.request.data, partial=True)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_valid_response(serializer), status=status.HTTP_200_OK)

    def get(self, request, pk):
        try:
            item_obj = self.get_object(pk)
            if not item_obj:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            serializer = GedFolderOrDocumentSerializer(item_obj, data=self.request.data, partial=True)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_valid_response(serializer), status=status.HTTP_200_OK)


class MoveToTrashDocumentFolderApi(views.APIView):
    """
    WHen someone delete document or folder those things goes to trash and only Contract administrator can remove them
    """
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
    """
        This api for Sourcing director to see all employee documents and folders.
    """
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector)

    def get_queryset(self):
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent').filter(
            is_trashed=False, organization_id=self.request.user.organization.id,
        )

    def get_filter(self):
        params = self.request.query_params
        selected_user = params.get('user')
        if not selected_user:
            return None
        queryset = self.get_queryset().filter(creator_id=selected_user)
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
            if not filtered_queryset:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            serializer = ListFolderOrDocumentSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(make_pagination(request, serializer, filtered_queryset), status=status.HTTP_200_OK)


class RemoveTrashOrDeleteFolderOrDocumentApi(views.APIView):
    """ This api for remove folder or document from trash or delete. Only Contract administrator can do it """

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
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent').filter(
            is_trashed=True, organization_id=self.request.user.organization.id
        )

    def get_filter(self):
        queryset = self.get_queryset()
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
    """  Give access for inside or outside users """
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = GiveAccessToDocumentFolder.objects.select_related(
            'organization', 'creator', 'user', 'folder_or_document'
        ).filter(organization_id=self.request.user.organization.id, folder_or_document__is_trashed=False)
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

    def delete_my_invites(self):
        my_invites = self.request.data
        user = self.request.user
        with transaction.atomic():
            for my_invite in my_invites:
                invite_obj = self.get_queryset().filter(id=my_invite, creator_id=user.id).first()
                if not invite_obj:
                    return f'{my_invite} not found.'
                invite_obj.delete()

    def validate_email(self, email):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def get_filtered_queryset(self):
        user = self.request.user
        params = self.request.query_params
        inside_user = params.get('user')
        outside_user = params.get('email')
        if inside_user:
            try:
                invited_user = int(inside_user)
            except ValueError:
                return 'Send only user id.'
            return self.get_queryset().filter(creator_id=user.id, user_id=invited_user)
        if outside_user:
            if not self.validate_email(outside_user):
                return f"{outside_user} is not valid email"
            return self.get_queryset().filter(creator_id=user.id, out_side_person=outside_user)
        return 'Send user=`ID` or email=`email` in the params.'

    def give_access_for_user(
            self, users: list, folders_or_documents: list, editable: bool, expiration_date: str,
    ):
        with transaction.atomic():
            creator = self.request.user
            documents_and_folders = FolderOrDocument.objects.select_related('organization', 'creator', 'parent')
            users_obj = User.objects.select_related('organization')
            email_and_tokens = []
            for user in users:
                if isinstance(user, str):
                    out_side_person = self.validate_email(user)
                    if not out_side_person:
                        raise f"{user} is not valid email"
                    access_cart = GiveAccessCart.objects.create(
                        organization_id=creator.organization.id,
                        creator_id=creator.id,
                        out_side_person=user
                    )
                for folder_or_document in folders_or_documents:
                    folder_document = documents_and_folders.filter(id=folder_or_document).first()
                    if not folder_document:
                        raise f'{folder_or_document} is not valid document or folder.'
                    if isinstance(user, int):
                        user_obj = users_obj.filter(id=user).first()
                        if not user_obj:
                            raise ValidationError(message=f'{user} is not valid user id.')
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
                        folder_or_document_access_notification(creator.id, user, serializer.data.get('id'))
                    if isinstance(user, str):
                        data = {
                            'out_side_person': user,
                            'folder_or_document': folder_or_document,
                            'editable': editable,
                            'expiration_date': expiration_date,
                        }
                        serializer = ShareLinkGiveAccessToDocumentFolderSerializer(data=data)
                        if not serializer.is_valid():
                            return make_errors(serializer.errors)
                        serializer.save(
                            creator_id=creator.id, organization_id=creator.organization.id,
                            shared_link_cart_id=access_cart.id
                        )
                if isinstance(user, str):
                    token_and_email = {
                        'token': access_cart.access_code,
                        'email': user,
                        'cart_id': access_cart.id
                    }
                    email_and_tokens.append(token_and_email)
            if token_and_email:
                send_shared_link_email(email_and_tokens)
        return True

    def post(self, request):
        try:
            data = self.request.data
            access_users = data.get('users')
            folders_or_documents = data.get('folder_or_document')
            editable = data.get('editable')
            expiration_date = data.get('expiration_date')
            give_access = self.give_access_for_user(
                access_users, folders_or_documents, editable, expiration_date
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
            response = self.delete_my_invites()
            if isinstance(response, str):
                return Response(get_error_response(response), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(object_deleted_response(), status=status.HTTP_204_NO_CONTENT)


class GetOutsideInvitesApi(views.APIView):
    """ Get outside invites and inters folders or documents """
    permission_classes = (permissions.IsAuthenticated,)

    def get_given_access_queryset(self):
        """ Get GiveAccessToDocumentFolder model """
        return GiveAccessToDocumentFolder.objects.select_related(
            'organization', 'creator', 'user', 'folder_or_document'
        ).filter(
            organization_id=self.request.user.organization.id, user_id=self.request.user.id,
            folder_or_document__is_trashed=False
        )

    def get_folder_or_document_queryset(self):
        print('2')
        """ Get FolderOrDocument model """
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent').filter(
            organization_id=self.request.user.organization.id, is_trashed=False
        )

    def get_params(self):
        print('3')
        params = self.request.query_params
        inviter_id = params.get('inviter_id')
        invite_id = params.get('invite_id')
        item_id = params.get('item_id')
        if not inviter_id:
            return None
        try:
            inviter_id = int(inviter_id)
        except ValueError:
            return None
        if invite_id and item_id:
            try:
                invite_id = int(invite_id)
                item_id = int(item_id)
            except ValueError:
                return None
        return {
            'inviter_id': inviter_id,
            'invite_id': invite_id,
            'item_id': item_id,
        }

    def get_item_obj(self):
        params = self.get_params()
        if not params['item_id'] and not params['invite_id']:
            return None
        return self.get_folder_or_document_queryset().filter(
            id=params['item_id'], creator_id=params['inviter_id']
        ).first()

    def get_invite_obj(self):
        params = self.get_params()
        if not params['item_id'] and not params['invite_id']:
            return None
        return self.get_given_access_queryset().filter(
            id=params['invite_id'], creator_id=params['inviter_id']
        ).first()

    def get_objects_and_queryset(self):
        print('6')
        params = self.get_params()
        folder_or_document = self.get_folder_or_document_queryset()
        invite_obj = self.get_given_access_queryset().filter(id=params['invite_id'], user_id=self.request.user.id).first()
        item_obj = folder_or_document.filter(id=params['item_id'], creator_id=params['inviter_id']).first()
        if not folder_or_document or not invite_obj or not item_obj:
            return None
        return {
            'folder_or_document': folder_or_document,
            'invite_obj': invite_obj,
            'item_obj': item_obj,
        }

    def validate_item(self, access_folder_id: int, item_obj):
        print('7')
        """ Validate item object for know this is a child of invite object folder """
        if item_obj.parent:
            if item_obj.parent.id < access_folder_id:
                return False
            if item_obj.parent.id == access_folder_id:
                return True
        if item_obj.parent is None:
            return False
        else:
            return self.validate_item(access_folder_id, item_obj.parent)

    def get_filtered_data(self):
        print('8')
        params = self.get_params()
        if not params:
            return None
        if not params['invite_id'] and not params['item_id']:
            return {
                'queryset': self.get_given_access_queryset().filter(creator_id=params['inviter_id']),
                'serializer': ListOutsideGiveAccessToDocumentFolderSerializer
            }
        obj_and_query = self.get_objects_and_queryset()
        if not obj_and_query:
            return None
        if obj_and_query['invite_obj'].folder_or_document.id > obj_and_query['item_obj'].id:
            return None
        if obj_and_query['invite_obj'].folder_or_document.id == obj_and_query['item_obj'].id:
            return {
                'queryset': obj_and_query['folder_or_document'].filter(parent_id=obj_and_query['item_obj'].id),
                'serializer': ListFolderOrDocumentSerializer,
                'invite': obj_and_query['invite_obj'],
            }
        else:
            if self.validate_item(obj_and_query['invite_obj'].folder_or_document.id, obj_and_query['item_obj']):
                return {
                    'queryset': obj_and_query['folder_or_document'].filter(parent_id=obj_and_query['item_obj'].id),
                    'serializer': ListFolderOrDocumentSerializer,
                    'invite': obj_and_query['invite_obj'],
                }

    def check_item_for_update(self, item_obj):
        invite_obj = self.get_invite_obj()
        if not item_obj or not invite_obj or item_obj.id < invite_obj.folder_or_document_id:
            return None
        if item_obj.id == invite_obj.folder_or_document_id:
            return True
        else:
            return self.validate_item(invite_obj.folder_or_document_id, item_obj)

    def get(self, request):
        try:
            outside_invites_and_folders = self.get_filtered_data()
            if not outside_invites_and_folders:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            if not outside_invites_and_folders.get('invite'):
                serializer = outside_invites_and_folders['serializer']
                queryset = outside_invites_and_folders['queryset']
                return Response(make_pagination(request, serializer, queryset))
            serializer = outside_invites_and_folders['serializer']
            queryset = outside_invites_and_folders['queryset']
            response = make_pagination(request, serializer, queryset)
            response['invite_obj'] = {
                'invite_id': outside_invites_and_folders['invite'].id,
                'invited_user': outside_invites_and_folders['invite'].creator.id,
                'editable': outside_invites_and_folders['invite'].editable,
                'expiration_date': outside_invites_and_folders['invite'].expiration_date,
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            item_obj = self.get_item_obj()
            check_item = self.check_item_for_update(item_obj)
            if not check_item:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            serializer = UpdateOutsideInvitesDocumentFolderSerializer(item_obj, data=self.request.data, partial=True)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer), status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(get_valid_response(), status=status.HTTP_200_OK)


class FolderDocumentUsersApi(views.APIView):
    """ This api for get users who have folders or invited users or outside invited users """
    permission_classes = (permissions.IsAuthenticated,)

    def remove_duplicated_user(self, queryset):
        data = []
        single_item = []
        with transaction.atomic():
            for q in queryset:
                if q.user.id not in single_item:
                    single_item.append(q.user.id)
                    data.append(q)
        return data

    def remove_duplicated_out_side_person(self, queryset):
        data = []
        single_item = []
        with transaction.atomic():
            for q in queryset:
                if q.out_side_person not in single_item:
                    single_item.append(q.out_side_person)
                    data.append(q)
        return data

    def sort_listed_queryset(self, queryset_list):
        with transaction.atomic():
            for i in range(len(queryset_list)):
                for x in range(i+1, len(queryset_list)):
                    if queryset_list[i].id < queryset_list[x].id:
                        queryset_list[i], queryset_list[x] = queryset_list[x], queryset_list[i]

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
                    return {
                        'queryset': self.get_queryset().filter(folder_creator__isnull=False).distinct(),
                        'serializer': FolderDocumentUsersSerializer
                    }
                case 'my_invites':
                    queryset_invites = GiveAccessToDocumentFolder.objects.select_related(
                        'organization', 'creator', 'user', 'folder_or_document',
                    ).filter(creator_id=user.id)
                    invites_in = self.remove_duplicated_user(queryset_invites.filter(user__isnull=False))
                    invites_out = self.remove_duplicated_out_side_person(queryset_invites.filter(user__isnull=True,))
                    my_invites = list(chain(invites_in, invites_out))
                    self.sort_listed_queryset(my_invites)
                    return {
                        'queryset': my_invites,
                        'serializer': UsersGiveAccessToDocumentFolderSerializer
                    }
                case 'outside_invites':
                    queryset = self.get_queryset().filter(
                        access_creator__user_id=user.id, access_creator__isnull=False
                    ).distinct()
                    return {
                        'queryset': queryset,
                        'serializer': FolderDocumentUsersSerializer
                    }
        else:
            return 'send users=general `or` my_invites `or` outside_invites, in the params.'

    def get(self, request):
        try:
            data = self.get_users()
            if isinstance(data, str):
                return Response(get_error_response(data), status=status.HTTP_400_BAD_REQUEST)
            queryset = data.get('queryset')
            serializer = data.get('serializer')
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(make_pagination(request, serializer, queryset))


class GetInsideInvitesFolderOrDocument(views.APIView):
    """
    This api to see folder or document which i give access to users and outside users
    in get request and patch request requires `invited user id and invited object id and item id - 'folder or document'`
    """

    def get_folder_or_document_queryset(self):
        """ Get FolderOrDocument model """
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent').filter(
            organization_id=self.request.user.organization.id, is_trashed=False
        )

    def get_given_access_queryset(self):
        """ Get GiveAccessToDocumentFolder model """
        return GiveAccessToDocumentFolder.objects.select_related(
            'organization', 'creator', 'user', 'folder_or_document'
        ).filter(
            organization_id=self.request.user.organization.id, creator_id=self.request.user.id,
            folder_or_document__is_trashed=False
        )

    def validate_email(self, email):
        """ Validation email """
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def get_params(self):
        """ Getting params and checking """
        params = self.request.query_params
        invite_id = params.get('invite_id')
        item_id = params.get('item_id')
        if not invite_id or not item_id:
            return None
        try:
            invite_id = int(invite_id)
        except ValueError:
            return None
        return {
            'invite_id': invite_id,
            'item_id': item_id
        }

    def get_objects_and_queryset(self):
        """ For getting folders queryset and invite object and also item object which user requested """
        params = self.get_params()
        if not params:
            return None
        folder_or_document = self.get_folder_or_document_queryset()
        invite_obj = self.get_given_access_queryset().filter(id=params['invite_id']).first()
        item_obj = folder_or_document.filter(id=params['item_id']).first()
        if not folder_or_document or not invite_obj or not item_obj:
            return None
        return {
            'folder_or_document': folder_or_document,
            'invite_obj': invite_obj,
            'item_obj': item_obj,
        }

    def validate_item(self, access_folder_id: int, item_obj):
        """ Validate item object for know this is a child of invite object folder """
        if item_obj.parent:
            if item_obj.parent.id < access_folder_id:
                return False
            if item_obj.parent.id == access_folder_id:
                return True
        if item_obj.parent is None:
            return False
        else:
            return self.validate_item(access_folder_id, item_obj.parent)

    def get_item_items(self):
        """
        if requested item is really child of invite object folder or its own, it will return children of requested item.
        """
        obj_and_query = self.get_objects_and_queryset()
        if not obj_and_query:
            return None
        if obj_and_query['invite_obj'].folder_or_document.id > obj_and_query['item_obj'].id:
            return None
        if obj_and_query['invite_obj'].folder_or_document.id == obj_and_query['item_obj'].id:
            return {
                'queryset': obj_and_query['folder_or_document'].filter(parent_id=obj_and_query['item_obj'].id),
                'invite': obj_and_query['invite_obj'],
            }
        else:
            if self.validate_item(obj_and_query['invite_obj'].folder_or_document.id, obj_and_query['item_obj']):
                return {
                    'queryset': obj_and_query['folder_or_document'].filter(parent_id=obj_and_query['item_obj'].id),
                    'invite': obj_and_query['invite_obj'],
                }

    def get(self, request):
        try:
            data = self.get_item_items()
            if not data:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            queryset = data.get('queryset')
            serializer = ListFolderOrDocumentSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        response = make_pagination(request, serializer, queryset)
        response['invite_obj'] = {
            'invite_id': data['invite'].id,
            'invited_user': data['invite'].user.id if data['invite'].user else data['invite'].out_side_person,
            'editable': data['invite'].editable,
            'expiration_date': data['invite'].expiration_date,
        }
        return Response(response, status=status.HTTP_200_OK)


class GetOutsideFolderOrDocument(views.APIView):
    """
    This api to see folder or document which i give access to users and outside users or invites
    in get request and patch request requires `invited user id and invited object id and item id - 'folder or document'`
    """

    def get_folder_or_document_queryset(self):
        """ Get FolderOrDocument model """
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent').filter(
            organization_id=self.request.user.organization.id, is_trashed=False
        )

    def get_given_access_queryset(self):
        """ Get GiveAccessToDocumentFolder model """
        return GiveAccessToDocumentFolder.objects.select_related(
            'organization', 'creator', 'user', 'folder_or_document'
        ).filter(organization_id=self.request.user.organization.id)

    def validate_email(self, email):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def get_params(self):
        params = self.request.query_params
        invite_id = params.get('invite_id')
        invited_user = params.get('invited_user')
        item_id = params.get('item_id')
        if not invite_id or not invited_user or not item_id:
            return None
        try:
            invite_id = int(invite_id)
            if self.validate_email(invited_user):
                invited_user = invited_user
            else:
                invited_user = int(invited_user)
            item_id = int(item_id)
        except ValueError:
            return None
        return {
            'invite_id': invite_id,
            'invited_user': invited_user,
            'item_id': item_id
        }

    def get_given_access_object(self):
        """ Get GiveAccessToDocumentFolder model object """
        params = self.get_params()
        if not params:
            return None
        if isinstance(params['invited_user'], str):
            return self.get_given_access_queryset().filter(
                id=params['invite_id'], out_side_person=params['invited_user']
            ).first()
        return self.get_given_access_queryset().filter(id=params['invite_id'], user_id=params['invited_user']).first()

    def get_folder_or_document_object(self):
        """ Get FolderOrDocument model object """
        params = self.get_params()
        if not params:
            return None
        return self.get_folder_or_document_queryset().filter(id=params['item_id']).first()

    def get_objects_and_queryset(self):
        folder_or_document = self.get_folder_or_document_queryset()
        invite_obj = self.get_given_access_object()
        item_obj = self.get_folder_or_document_object()
        if not folder_or_document or not invite_obj or not item_obj:
            return None
        return {
            'folder_or_document': folder_or_document,
            'invite_obj': invite_obj,
            'item_obj': item_obj,
        }

    def validate_item(self):
        """ This function validate item is children of folder in the invited object """
        obj_and_query = self.get_objects_and_queryset()
        if not obj_and_query:
            return None
        if obj_and_query['invite_obj'].folder_or_document.id > obj_and_query['item_obj'].id:
            return None
        for f_o_d in obj_and_query['folder_or_document'].filter(
                id__lte=obj_and_query['item_obj'].id, creator_id=obj_and_query['invite_obj'].creator.id
        ).order_by('-id'):
            if f_o_d.id == obj_and_query['invite_obj'].folder_or_document.id:
                return True
            if f_o_d.parent_id == obj_and_query['invite_obj'].folder_or_document.id:
                return True
            return None

    def get_item_items(self):
        """ return children of that item """
        validated_item_query = self.validate_item()
        item_and_invite = self.get_objects_and_queryset()
        if not validated_item_query:
            return None
        return {
            'queryset': item_and_invite['folder_or_document'].filter(parent_id=item_and_invite['item_obj'].id),
            'invite': item_and_invite['invite_obj'],
        }

    def get(self, request):
        try:
            data = self.get_item_items()
            if not data:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            queryset = data.get('queryset')
            serializer = ListFolderOrDocumentSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        response = make_pagination(request, serializer, queryset)
        response['invite_obj'] = {
            'invite_id': data['invite'].id,
            'invited_user': data['invite'].user.id if data['invite'].user else data['invite'].out_side_person,
            'editable': data['invite'].editable,
            'expiration_date': data['invite'].expiration_date,
        }
        return Response(response, status=status.HTTP_200_OK)


class SharedLinkAPi(views.APIView):
    """ This api for users who have received share ink email message """

    def get_given_access_queryset(self):
        return GiveAccessToDocumentFolder.objects.select_related('organization', 'creator', 'user', 'folder_or_document')

    def give_access_cart_queryset(self):
        return GiveAccessCart.objects.select_related('organization', 'creator')

    def get_user_queryset(self):
        return User.objects.select_related('organization').filter(
            cart_creator__out_side_person=self.get_cart().out_side_person
        )

    def get_params(self):
        params = self.request.query_params
        token = params.get('token')
        method = params.get('method')
        user_carts = params.get('user_carts')
        item_id = params.get('item_id')
        cart_id = params.get('cart_id')
        if not token:
            return None
        if item_id:
            try:
                item_id = int(item_id)
            except ValueError:
                return None
        if cart_id:
            try:
                cart_id = int(cart_id)
            except ValueError:
                return None
        return {
            'token': token,
            'item_id': item_id,
            'method': method,
            'user_carts': user_carts,
            'cart_id': cart_id,
        }

    def get_cart(self):
        token = self.get_params().get('token')
        return GiveAccessCart.objects.select_related('organization', 'creator').filter(access_code=token).first()

    def check_token(self):
        params = self.get_params()
        if not params:
            return None
        given_access_queryset = self.get_given_access_queryset().filter(access_code=params['token']).first()
        if not given_access_queryset:
            return None
        return given_access_queryset

    def get_folder_or_document_queryset(self):
        token = self.check_token()
        if not token:
            return None
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent').filter(
            creator_id=token.creator_id,
        )

    def check_item_id(self):
        params = self.get_params()
        token = self.check_token()
        if not token or not params['item_id']:
            return None
        return self.get_folder_or_document_queryset().filter(id=params['item_id']).first()

    def check_item_parent(self, access_folder_id: int, item_obj):
        """ Validate item object for know this is a child of invite object folder """
        if item_obj.parent:
            if item_obj.parent.id < access_folder_id:
                return False
            if item_obj.parent.id == access_folder_id:
                return True
        if item_obj.parent is None:
            return False
        else:
            return self.check_item_parent(access_folder_id, item_obj.parent)

    def validate_item(self):
        token = self.check_token()
        item_obj = self.check_item_id()
        if not token or not item_obj:
            return None
        if token.folder_or_document_id > item_obj.id:
            return None
        if token.folder_or_document_id == item_obj.id:
            return {
                'queryset': self.get_folder_or_document_queryset().filter(parent_id=item_obj.id)
            }
        else:
            check_item = self.check_item_parent(token.folder_or_document_id, item_obj)
            if not check_item:
                return None
            return {
                'queryset': self.get_folder_or_document_queryset().filter(parent_id=item_obj.id)
            }

    def get(self, request):
        try:
            params = self.get_params()
            invite_obj = self.check_token()
            if not params:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            if params.get('method') == 'main_page':
                users = self.get_user_queryset().distinct()
                serializer = FolderDocumentUsersSerializer
                return Response(make_pagination(request, serializer, users), status=status.HTTP_200_OK)
            if params.get('user_carts'):
                inviter = self.get_user_queryset().get(id=int(params.get('user_carts')))
                inviter_shared_links = self.give_access_cart_queryset().filter(creator_id=inviter.id)
                serializer = GiveAccessCartSharedSerializer
                return Response(make_pagination(request, serializer, inviter_shared_links), status=status.HTTP_200_OK)
            if params.get('cart_id'):
                folders = self.get_given_access_queryset().filter(shared_link_cart_id=int(params.get('cart_id')))
                serializer = SharedLinkListSerializer
                return Response(make_pagination(request, serializer, folders), status=status.HTTP_200_OK)
            if not params['item_id']:
                serializer = GetSharedLinkInviteSerializer(invite_obj)
                return Response(serializer_valid_response(serializer), status=status.HTTP_200_OK)
            validate_item = self.validate_item()
            if not validate_item:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            serializer = GetSharedLinkDocumentOrFolderSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            response = make_pagination(request, serializer, validate_item['queryset'])
            response['invite_obj'] = {
                'invite_id': invite_obj.id,
                'editable': invite_obj.editable,
            }
            return Response(response, status=status.HTTP_200_OK)

    def patch(self, request):
        """ Item_id and  """
        try:
            validate_item = self.validate_item()
            if not validate_item:
                return Response(object_not_found_response(), status=status.HTTP_400_BAD_REQUEST)
            item_obj = self.check_item_id()
            token = self.check_token()
            if not token.editable:
                return Response(
                    {
                        'success': False,
                        'message': 'Yo do not have access to perform this action.',
                        'error': 'Error occurred',
                        'data': []
                    }
                )
            serializer = GetSharedLinkDocumentOrFolderSerializer(item_obj, data=self.request.data, partial=True)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer), status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(get_valid_response(), status=status.HTTP_200_OK)
