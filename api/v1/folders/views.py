from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render
from rest_framework import generics, views, status, permissions
from django.db.models import Q
from rest_framework.response import Response
from .serializers import (
    PostFolderOrDocumentSerializer, ListFolderOrDocumentSerializer, PatchFolderOrDocumentSerializer,
    PatchAdministratorFolderOrDocumentSerializer, TrashedFolderOrDocumentSerializer,
)
from .models import (
    FolderOrDocument,
)
from ..commons.pagination import make_pagination
from ..commons.views import (
    exception_response, not_serializer_is_valid, serializer_valid_response, object_deleted_response,
)
from ..users.permissions import IsSourcingDirector, IsContractAdministrator
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
                return Response(not_serializer_is_valid(serializer.errors))
            serializer.save(created_id=user.id, organization_id=user.organization.id)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_valid_response(), status=status.HTTP_201_CREATED)

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
            if not serializer.is_valid:
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
            raise ValidationError('Select role')
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


