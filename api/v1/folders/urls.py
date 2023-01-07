from django.urls import path
from .views import (
    PostListFolderOrDocumentApi, ListUsersDocumentFolderAPI, PatchDeleteFolderOrDocumentApi,
    MoveToTrashDocumentFolderApi, RemoveTrashOrDeleteFolderOrDocumentApi, TrashedDocumentFolderApi
)


urlpatterns = [
    path('', PostListFolderOrDocumentApi.as_view()),
    path('move-trash/', MoveToTrashDocumentFolderApi.as_view()),
    path('remove-delete/', RemoveTrashOrDeleteFolderOrDocumentApi.as_view()),
    path('trashed/', TrashedDocumentFolderApi.as_view()),
    path('users/', ListUsersDocumentFolderAPI.as_view()),
    path('detail/<int:id>/', PatchDeleteFolderOrDocumentApi.as_view()),
]
