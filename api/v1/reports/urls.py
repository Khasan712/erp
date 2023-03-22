from django.urls import path

from .views import ReportAPi

urlpatterns = [
    path('', ReportAPi.as_view()),
]
