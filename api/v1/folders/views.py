from django.shortcuts import render
from rest_framework import generics, views, status, permissions
from django.db.models import Q
from rest_framework.response import Response
from .serializers import (
    PostFolderSerializer, ListFolderSerializer,
)
from .models import (
    Folder,
)
from ..commons.pagination import make_pagination
from ..commons.views import (
    exception_response, not_serializer_is_valid, serializer_valid_response,
)


# Create your views here.


class PostFolderApi(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Folder.objects.select_related('organization', 'creator')

    def get_filter(self):
        user = self.request.user
        queryset = self.get_queryset().filter(
            creator_id=user.id, is_trashed=False, parent__isnull=True, organization_id=user.organization.id
        )
        params = self.request.query_params
        q = params.get('q')
        parent_id = params.get('parent')
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(document_folder__document__icontains=q))
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        return queryset

    def post(self, request):
        try:
            serializer = PostFolderSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer.errors))
            serializer.save()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_valid_response(), status=status.HTTP_201_CREATED)

    def get(self, request):
        try:
            filtered_queryset = self.get_filter()
            serializer = ListFolderSerializer
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(make_pagination(request, serializer, filtered_queryset), status=status.HTTP_200_OK)


