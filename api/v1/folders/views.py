from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import generics, views, status, permissions
from django.db.models import Q
from rest_framework.response import Response
from .serializers import (
    PostFolderOrDocumentSerializer, ListFolderOrDocumentSerializer,
)
from .models import (
    FolderOrDocument,
)
from ..commons.pagination import make_pagination
from ..commons.views import (
    exception_response, not_serializer_is_valid, serializer_valid_response,
)
from ..users.permissions import IsSourcingDirector


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


class ListUsersDocumentFolderAPI(views.APIView):
    """ This API for Sourcing director to see all employee documents and folders """
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector)

    def get_queryset(self):
        return FolderOrDocument.objects.select_related('organization', 'creator', 'parent')

    def get_filter(self):
        params = self.request.query_params
        user = self.request.user
        role = params.get('role')
        if not role:
            raise ValidationError('Select role')
        queryset = self.get_queryset().filter(is_trashed=False, organization_id=user.organization.id, creator_id=role)
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

