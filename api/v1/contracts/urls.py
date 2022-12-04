from django.urls import path
from .views import (
    ContractListView,
    ContractListDetailView,
    MassUploadView,
    CategoryListView,
    CategoryListDetailView,
    DepartmentListView,
    DepartmentListDetailView,
    ContractTypeListView,
    ContractTypeListDetailView,
    CostCenterListDetailView,
    CostCenterListView,
    CurrencyListView,
    CurrencyListDetailView,
    ContractFileUpload,
    ContractStatusStatisticsView,
    ContractCategoryStatisticsView,
    ProcessContractTaskView,
    ContractDetailView
)

urlpatterns = [
    path('', ContractListView.as_view()),
    path('task/', ProcessContractTaskView.as_view()),
    path('detail/', ContractDetailView.as_view(), name='contract-detail'),
    path('status/', ContractStatusStatisticsView.as_view()),
    path('upload/<int:pk>/', ContractFileUpload.as_view()),
    path('currency/list/', CurrencyListView.as_view()),


    path('get/contract/<id>', ContractListDetailView.as_view()),
    path('mass/create', MassUploadView.as_view()),

    # category
    path('category/', CategoryListView.as_view()),
    path('category/spends/', ContractCategoryStatisticsView.as_view()),
    path('category/detail/<id>', CategoryListDetailView.as_view()),

    # department
    path('department/list/', DepartmentListView.as_view()),
    path('department/detail/<id>', DepartmentListDetailView.as_view()),

    # API for contract:

    path('contracttype', ContractTypeListView.as_view()),
    path('contracttype/detail/<id>', ContractTypeListDetailView.as_view()),

    #API for cost center
    path('costcenter', CostCenterListView.as_view()),
    path('costcenter/detail/<id>', CostCenterListDetailView.as_view()),

    # API for terms types
    path('currency', CurrencyListView.as_view()),
    path('currency/detail/<id>', CurrencyListDetailView.as_view())
]
