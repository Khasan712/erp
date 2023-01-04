from django.urls import path
from .views import (
    PostListFolderOrDocumentApi, ListUsersDocumentFolderAPI
)


urlpatterns = [
    path('', PostListFolderOrDocumentApi.as_view()),
    path('users/', ListUsersDocumentFolderAPI.as_view()),
]
