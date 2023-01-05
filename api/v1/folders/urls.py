from django.urls import path
from .views import (
    PostListFolderOrDocumentApi, ListUsersDocumentFolderAPI, PatchDeleteFolderOrDocumentApi
)


urlpatterns = [
    path('', PostListFolderOrDocumentApi.as_view()),
    path('users/', ListUsersDocumentFolderAPI.as_view()),
    path('detail/<int:id>/', PatchDeleteFolderOrDocumentApi.as_view()),
]
