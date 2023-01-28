from django.urls import path
from .views import (
    PostListFolderOrDocumentApi, ListUsersDocumentFolderAPI, PatchDeleteFolderOrDocumentApi,
    MoveToTrashDocumentFolderApi, RemoveTrashOrDeleteFolderOrDocumentApi, TrashedDocumentFolderApi,
    GiveAccessToDocumentFolderApi, GetOutsideInvitesApi, FolderDocumentUsersApi, GetInsideInvitesFolderOrDocument
)


urlpatterns = [
    path('', PostListFolderOrDocumentApi.as_view()),
    path('detail/<int:id>/', PatchDeleteFolderOrDocumentApi.as_view()),
    path('move-trash/', MoveToTrashDocumentFolderApi.as_view()),
    path('remove-delete/', RemoveTrashOrDeleteFolderOrDocumentApi.as_view()),
    path('trashed/', TrashedDocumentFolderApi.as_view()),
    path('users/', ListUsersDocumentFolderAPI.as_view()),
    path('give-access/', GiveAccessToDocumentFolderApi.as_view()),
    path('get-users/', FolderDocumentUsersApi.as_view()),
    path('inside-invites/', GetInsideInvitesFolderOrDocument.as_view()),
    path('outside-invites/', GetOutsideInvitesApi.as_view()),
]
