import os
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from django.db.models import Q, Sum, Avg, Count
from rest_framework.views import APIView
import pandas as pd
import openpyxl
import datetime
from rest_framework import status, permissions, generics
from docx2pdf import convert
from django.db import transaction
from asgiref.sync import sync_to_async
from rest_framework.decorators import api_view
from django.core.exceptions import ValidationError
import jwt

from api.v1.commons.pagination import make_pagination
from api.v1.commons.views import exception_response, get_serializer_errors, get_serializer_valid_response, \
    object_not_found_response, serializer_valid_response
from api.v1.users.models import User
from django.conf import settings
from api.v1.contracts.serializers import (
    ContractFileUploadSerializer,
    ContractSerializer,
    MassUploadSerializer,
    CategorySerializer,
    CurrencySerializer,
    ContractTypeSerializer,
    CostCenterSerializer,
    DepartementSerializer, DocumentContactSerializers, ContractTaskSerializers, ContractServiceSerializers,
    ContractCommoditySerializers, ContractConsultantSerializers, ContractListSerializers, ContractGetSerializer,
)
from api.v1.contracts.models import (
    Contract,
    Departement,
    Contract_Type,
    Category,
    Cost_Center,
    Currency, ContractTask, ConnectContractWithTask
)
from api.v1.users.services import make_errors
from api.v1.users.permissions import (
    IsAdmin,
    IsContractAdministrator,
    IsSourcingDirector, IsSupplier
)


# API for contracts :
class ContractStatusStatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector)

    def get_queryset(self):
        queryset = Contract.objects.select_related(
            'parent_agreement', 'departement', 'category', 'currency', 'organization', 'create_by', 'supplier'
        ).filter(organization_id=self.request.user.organization.id)
        return queryset

    def get(self, request):
        try:
            return Response(
                {
                    "success": True,
                    "message": 'Successfully got contracts status statistics.',
                    "error": [],
                    "data": {
                        'total':self.get_queryset().count(),
                        'active': self.get_queryset().filter(status='ACTIVE').count(),
                        'draft': self.get_queryset().filter(status='DRAFT').count(),
                        'expired': self.get_queryset().filter(status='EXPIRED').count()
                    },
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )


class ContractCategoryStatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector)

    def get_categories(self):
        categories = Category.objects.select_related('organization').filter(organization_id=self.request.user.organization.id)
        return categories

    def get(self, request):
        try:
            categories = self.get_categories().annotate(spends=Sum('contract__contract_amount')).values('name', 'spends')
            return Response(
                {
                    "success": True,
                    "message": 'Successfully got category statistics.',
                    "error": [],
                    "data": categories
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )


class ContractListView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsContractAdministrator | IsSourcingDirector)

    def get_queryset(self):
        queryset = Contract.objects.select_related('parent_agreement', 'departement', 'category', 'currency',
            'organization', 'create_by', 'supplier').filter(organization_id=self.request.user.organization.id)
        params = self.request.query_params
        contract_structure = params.get('contract_structure')
        category = params.get('category')
        currency = params.get('currency')
        terms = params.get('terms')
        contract_status = params.get('status')
        q = params.get('q')
        if contract_structure:
            queryset = queryset.filter(contract_structure__in=contract_structure.split(','))
        if category:
            queryset = queryset.filter(category_id__in=category.split(','))
        if currency:
            queryset = queryset.filter(currency_id__in=currency.split(','))
        if terms:
            queryset = queryset.filter(terms__in=terms.split(','))
        if contract_status:
            queryset = queryset.filter(status__in=contract_status.split(','))
        if q:
            queryset = queryset.filter(
                Q(duration__icontains=q) | Q(name__icontains=q) | Q(contract_number__icontains=q) |
                Q(description__icontains=q) | Q(contract_structure__icontains=q) | Q(contract_amount__icontains=q) |
                Q(category__name__icontains=q) | Q(currency__name__icontains=q) | Q(terms__icontains=q) |
                Q(status__icontains=q) | Q(supplier__name__icontains=q)
            )
        return queryset

    def create_service_choices(self, service_choice, items, contract_id):
        creator = self.request.user.id
        with transaction.atomic():
            match service_choice:
                case 'service':
                    for service in items:
                        service['service'] = service.get('id')
                        service_serializer = ContractServiceSerializers(data=service)
                        if not service_serializer.is_valid():
                            get_serializer_errors(service_serializer)
                        service_serializer.save(contract_id=contract_id, creator_id=creator)
                case 'commodity':
                    for commodity in items:
                        commodity['commodity'] = commodity.get('id')
                        commodity_serializer = ContractCommoditySerializers(data=commodity)
                        if not commodity_serializer.is_valid():
                            get_serializer_errors(commodity_serializer)
                        commodity_serializer.save(contract_id=contract_id, creator_id=creator)
                case 'consultant':
                    for consultant in items:
                        consultant['consultant'] = consultant.get('id')
                        consultant_serializer = ContractConsultantSerializers(data=consultant)
                        if not consultant_serializer.is_valid():
                            get_serializer_errors(consultant_serializer)
                        consultant_serializer.save(contract_id=contract_id, creator_id=creator)

    def validate_contract_structure(self, data):
        contract_structure = data.get('contract_structure')
        match contract_structure:
            case 'Stand Alone':
                if data.get('parent_agreement') is not None:
                    return 'Can not be parent agreement.'
            case 'Master Agreement':
                if data.get('parent_agreement') is not None:
                    return 'Can not be parent agreement.'
            case 'Sub Agreement':
                if data.get('parent_agreement') is None:
                    return 'Choose parent agreement.'
                if data.get('parent_agreement') is not None:
                    contract_structure_of_parent_agreement = self.get_queryset().get(id=data.get('parent_agreement'))
                    if contract_structure_of_parent_agreement.contract_structure != 'Master Agreement':
                        return 'Contract structure must be Master Agreement in Parent agreement.'
            case '':
                return 'Choose contract structure.'
        return True

    def get(self, request):
        try:
            return Response(
                make_pagination(self.request, ContractListSerializers, self.get_queryset()), status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        try:
            if self.request.user.role != 'contract_administrator':
                return Response(
                    {
                        'success': False,
                        'message': 'You do not have permission.',
                        'error': 'Error occurred.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            data = self.request.data
            service_choice = data.get('serviceCommodityConsultant')
            items = data.get('items')
            with transaction.atomic():
                if self.validate_contract_structure(data) is not True:
                    raise ValidationError(self.validate_contract_structure(data))
                serializer = ContractSerializer(data=data)
                if not serializer.is_valid():
                    raise ValidationError(message=f'{make_errors(serializer.errors)}')
                serializer.save(create_by_id=self.request.user.id, organization_id=self.request.user.organization.id)
                if data.get('documents'):
                    for document in data.get('documents'):
                        document['contract'] = serializer.data.get('id')
                        doc_serializer = DocumentContactSerializers(data=document)
                        if not doc_serializer.is_valid():
                            raise ValidationError(message=f'{make_errors(doc_serializer.errors)}')
                        doc_serializer.save()
                if not items and service_choice:
                    raise ValidationError(message="Please select any choices!")
                if service_choice and items:
                    self.create_service_choices(service_choice, items, serializer.data.get('id'))
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                serializer_valid_response(serializer), status=status.HTTP_201_CREATED
            )


class ContractDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector | IsContractAdministrator)

    def get_queryset(self):
        queryset = Contract.objects.select_related('parent_agreement', 'departement', 'category', 'currency',
            'organization', 'create_by', 'supplier').filter(organization_id=self.request.user.organization.id)
        return queryset

    def get_object(self):
        contract_id = self.request.query_params.get('contract')
        return self.get_queryset().filter(id=contract_id).first()

    def update_contract_tasks(self, tasks: list, contract_id: int):
        contract_tasks = ConnectContractWithTask.objects.select_related('contract', 'task', 'executor', 'checker').filter(
            contract_id=contract_id
        )
        with transaction.atomic():
            for task in tasks:
                contract_task = contract_tasks.filter(id=task.get('id')).first()
                contract_task.is_done = task.get('is_done')
                contract_task.save()

    def get(self, request):
        try:
            if self.get_object() is None:
                return Response(object_not_found_response())
            serializer = ContractGetSerializer(self.get_object())
            return Response(get_serializer_valid_response(serializer))
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request):
        try:
            if self.get_object() is None:
                return Response(
                    {
                        "success": False,
                        "message": 'Error occurred.',
                        "error": 'Contract not found.',
                        "data": [],
                    }
                )
            data = self.request.data
            contract_tasks = data.get('tasks')
            service_commodity_consultant = data.get('serviceCommodityConsultant')
            items = data.get('items')
            serializer = ContractSerializer(self.get_object(), data=data, partial=True)
            with transaction.atomic():
                if not serializer.is_valid():
                    raise get_serializer_errors(serializer)
                serializer.save()
                if contract_tasks is not None:
                    self.update_contract_tasks(contract_tasks, serializer.data.get('id'))

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "success": True,
                "message": 'Successfully updated Contract.',
                "error": [],
                "data": serializer.data,
            }, status=status.HTTP_200_OK
        )


class ProcessContractTaskView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            with transaction.atomic():
                is_done = False
                contract = Contract.objects.select_related(
                    'parent_agreement', 'departement', 'category', 'currency', 'organization', 'create_by', 'supplier'
                )
                for task in self.request.data.get('tasks'):
                    task_id = ContractTask.objects.select_related('creator', 'contract', 'executor', 'checker').filter(
                        id=task['id'], contract__organization_id=self.request.user.organization.id
                    ).first()
                    contract = contract.filter(organization_id=self.request.user.orhanization.id, id=task.get('contract')).first()
                    if not contract:
                        raise ValidationError(message="Task not found.")
                    serializer = ContractTaskSerializers(task_id, data=task, partial=True)
                    if not serializer.is_valid():
                        raise ValidationError(message=f'{make_errors(serializer.errors)}')
                    is_done = task.get('is_done')
                    serializer.save(checker_id=self.request.user.id)
                # if is_done:
                #     contract.status = 'ACTIVE'
                #     contract.save()
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "success": True,
                "message": 'Successfully done task events.',
                "error": [],
                "data": [],
            }, status=status.HTTP_201_CREATED
        )


class ContractFileUpload(generics.UpdateAPIView):
    queryset = Contract.objects.select_related('parent_agreement', 'departement', 'category', 'currency', 'organization', 'create_by', 'supplier')
    serializer_class = ContractFileUploadSerializer
    
    def patch(self, request, pk, *args, **kwargs):
        item = Contract.objects.get(id=pk)
        item.document = request.data.get('document')
        item.save()
        item.document = convert(os.path.abspath(item.document.path))
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)


class CurrencyListView(generics.ListCreateAPIView):
    queryset = Currency.objects.select_related('organization')
    serializer_class = CurrencySerializer

    def get(self, request):
        try:
            currencies = self.get_queryset().filter(organization_id=self.request.user.organization.id)
            serializer = self.get_serializer(currencies, many=True)
            return Response(
                {
                    "success": True,
                    "message": 'Service got successfully.',
                    "error": [],
                    "data": serializer.data,
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):

        serializer = CurrencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization = request.user.organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrencyListDetailView(APIView):

    def get(self, request, id):
        queryset = Currency.objects.filter(organization = request.user).get(id=id)
        serializer = CurrencySerializer(queryset)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def put(self, request, id):
        queryset = Currency.objects.filter(organization = request.user).get(id=id)
        serializer = CurrencySerializer(queryset, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = Currency.objects.filter(organization = request.user).get(id=id)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# API for cost center

class CostCenterListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        queryset = Cost_Center.objects.filter(organization = request.user)
        serializer = CostCenterSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def post(self, request):

        serializer = CostCenterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization = request.user.organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CostCenterListDetailView(APIView):

    def get(self, request, id):
        queryset = Cost_Center.objects.filter(organization = request.user).get(id=id)
        serializer = CostCenterSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def put(self, request, id):
        queryset = Cost_Center.objects.filter(organization = request.user).get(id=id)
        serializer = CostCenterSerializer(queryset, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = Cost_Center.objects.filter(organization = request.user).get(id=id)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#API for contract type :

class ContractTypeListView(APIView):

    def get(self, request):
        queryset = Contract_Type.objects.filter(organization = request.user)
        serializer = ContractTypeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def post(self, request):

        serializer = ContractTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization = request.user.organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractTypeListDetailView(APIView):

    def get(self, request, id):
        queryset = Contract_Type.objects.filter(organization = request.user).get(id=id)
        serializer = ContractTypeSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def put(self, request, id):
        queryset = Contract_Type.objects.filter(organization = request.user).get(id=id)
        serializer = ContractTypeSerializer(queryset, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = Contract_Type.objects.filter(organization = request.user).get(id=id)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# API for department :
class DepartmentListView(generics.ListCreateAPIView):
    queryset = Departement.objects.select_related('organization', 'creator')
    serializer_class = DepartementSerializer

    def get(self, request):
        try:
            departments = self.get_queryset().filter(organization_id=self.request.user.organization.id)
            serializer = self.get_serializer(departments, many=True)
            return Response(
                {
                    "success": True,
                    "message": 'Department got successfully.',
                    "error": [],
                    "data": serializer.data,
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):

        serializer = DepartementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization = request.user.organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartmentListDetailView(APIView):

    def get(self, request, id):
        queryset = Departement.objects.filter(organization = request.user).get(id=id)
        serializer = DepartementSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def put(self, request, id):
        queryset = Departement.objects.filter(organization = request.user).get(id=id)
        serializer = DepartementSerializer(queryset, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = Departement.objects.filter(organization = request.user).get(id=id)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# APi for category :
class CategoryListView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector | IsContractAdministrator | IsSupplier)

    def get_queryset(self):
        queryset = Category.objects.select_related('organization').filter(
            organization_id=self.request.user.organization.id)
        return queryset

    def get(self, request):
        try:
            return Response(make_pagination(self.request, CategorySerializer, self.get_queryset()))
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization = request.user.organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListDetailView(APIView):

    def get(self, request, id):
        queryset = Category.objects.filter(organization = request.user).get(id=id)
        serializer = CategorySerializer(queryset)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def put(self, request, id):
        queryset = Category.objects.filter(organization = request.user).get(id=id)
        serializer = CategorySerializer(queryset, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = Category.objects.filter(organization = request.user).get(id=id)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContractListDetailView(APIView):

    def get(self, request, id):
        con = Contract.objects.filter(organization = request.user).get(id=id)
        serializer = ContractSerializer(con)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        con = Contract.objects.filter(organization = request.user).get(id=id)
        serializer = ContractSerializer(con, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        con = Contract.objects.filter(organization = request.user).get(id=id)
        con.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class MassUploadView(APIView):

    def post(self, request):
        serializer = MassUploadSerializer(data = request.data)
        file = request.data['file']
        file = pd.read_excel(file)
        file = pd.DataFrame(data=file)
        for i in range(0, len(file)):
            Contract.objects.create(name= file.iloc[i][0], description=file.iloc[i][1], organization=request.user.organization)
        return Response("ok")




