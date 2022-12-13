from django.urls import path
from api.v1.suppliers.views import (
    SupplierListView,
    SupplierMassCreate,
    SuppliersDetail,
    SuppliersQuestionaryView,
    SupplierQuestionaryAnswerView,
    SupplierStatisticsView,
    GetContractsBySupplierID
)

urlpatterns = [
    path('', SupplierListView.as_view()),
    path('detail/<int:pk>/', SuppliersDetail.as_view()),
    path('questionary/', SuppliersQuestionaryView.as_view()),
    path('answers/', SupplierQuestionaryAnswerView.as_view()),
    path('statistics/', SupplierStatisticsView.as_view()),
    path('contracts/', GetContractsBySupplierID.as_view()),
    path('masscreate', SupplierMassCreate.as_view()),
]
