from django.urls import path
from .views import (
    ChatListView,
)


urlpatterns = [
    path('', ChatListView.as_view()),
]
