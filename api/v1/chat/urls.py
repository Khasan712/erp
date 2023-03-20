from django.urls import path

from api.v1.chat.views import ChatApi

urlpatterns = [
    path('', ChatApi.as_view()),
]
