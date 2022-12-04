from django.urls import path
from api.v1.organization.views import OrganizationListView, OrganizationDetailListView

urlpatterns = [
    path('list', OrganizationListView.as_view()),
    path('get/detail/<id>', OrganizationDetailListView.as_view())
]
