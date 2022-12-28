from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from api.v1.users.models import User
from api.v1.commons.pagination import make_pagination
from api.v1.commons.views import exception_response, get_serializer_valid_response, not_serializer_is_valid, \
    serializer_valid_response, object_deleted_response, object_not_found_response
from api.v1.users.services import make_errors
from .serializers import (
    SupplierSerializer,
    SupplierMasCreateSerializer,
    SupplierQuestionarySerializer,
    QuestionarySuppliersSerializers,
    SQCategorySerializer,
    SQCQuestionSerializer,
    QuestionaryAnswerSerializers,
    QuestionaryCheckSerializers,
    SupplierDetailSerializers,
    SupplierGetSerializer
)
from rest_framework import generics, status, permissions
from .models import (
    Supplier,
    SupplierQuestionaryResult,
    SupplierQuestionaryAnswer,
    SupplierQuestionary,
    SupplierComments
)
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import openpyxl
import random
from django.db import transaction
from django.core.exceptions import ValidationError
from api.v1.chat.views import (
    send_alert_supplier_questionary,
    send_result_notification
)
from api.v1.users.permissions import (
    IsSourcingDirector, IsContractAdministrator, IsSupplier,
)
from ..contracts.models import Contract
from ..contracts.serializers import ContractGetSerializer
from ..sourcing.models import SourcingRequestEventSuppliers, SourcingRequestEvent
from ..sourcing.serializers import GetSupplierSourcingEvents


class SupplierListView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsContractAdministrator | IsSourcingDirector)

    def get_queryset(self):
        queryset = Supplier.objects.select_related('organization', 'create_by', 'supplier', 'parent').filter(
            organization_id=self.request.user.organization.id
        )
        params = self.request.query_params
        q = params.get('q')
        supplier_status = params.get('status')
        if q is not None:
            queryset = queryset.filter(
                Q(parent_supplier__first_name__icontains=q) | Q(parent_supplier__last_name__icontains=q) | Q(name__icontains=q) |
                Q(account__icontains=q) | Q(address__icontains=q) | Q(city__icontains=q) | Q(postal_code__icontains=q)
                | Q(country__icontains=q) | Q(supplier_status__icontains=q) | Q(bank_name__icontains=q) |
                Q(transit_number__icontains=q) | Q(institution_number__icontains=q) | Q(bank_account__icontains=q)
            )
        if supplier_status is not None:
            queryset = queryset.filter(supplier_status__in=supplier_status.split(','))
        return queryset

    def get(self, request):
        try:
            return Response(
                make_pagination(self.request, SupplierGetSerializer, self.get_queryset()),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            if request.data.get('same_billing_address') is True and request.data.get('parent') is not None:
                parent_billing_address = self.get_queryset().get(id=request.data.get('parent'))
                request.data['billing_address'] = parent_billing_address.billing_address
            serializer = SupplierSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(not_serializer_is_valid(serializer), status=status.HTTP_400_BAD_REQUEST)
            serializer.save(organization_id=self.request.user.organization.id, create_by_id=self.request.user.id)
            return Response(get_serializer_valid_response(serializer), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)


class SuppliersDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector | IsContractAdministrator)

    def get_queryset(self):
        queryset = Supplier.objects.select_related('organization', 'create_by', 'supplier', 'parent').filter(
            organization_id=self.request.user.organization.id
        )
        return queryset

    def get_object(self, pk: int):
        return self.get_queryset().filter(id=pk).first()

    def get(self, request, pk):
        try:
            supplier = self.get_object(pk)
            if supplier is None:
                return Response(object_not_found_response(), status=status.HTTP_204_NO_CONTENT)
            supplier_serializer = SupplierDetailSerializers(supplier)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(
            get_serializer_valid_response(supplier_serializer), status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        try:
            supplier = self.get_object(pk)
            if supplier is None:
                return Response(object_not_found_response(), status=status.HTTP_204_NO_CONTENT)
            supplier_serializer = SupplierDetailSerializers(supplier, data=self.request.data, partial=True)
            if not supplier_serializer.is_valid():
                return Response(not_serializer_is_valid(supplier_serializer), status=status.HTTP_400_BAD_REQUEST)
            supplier_serializer.save()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(
            serializer_valid_response(supplier_serializer), status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        try:
            supplier = self.get_object(pk)
            supplier.delete()
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(
            object_deleted_response(), status=status.HTTP_204_NO_CONTENT
        )


# The code is working fine :) i must work on thecode to make it more performant
class SupplierMassCreate(APIView):
    def post(self, request):
        serializer = SupplierMasCreateSerializer(data = request.data)
        file = request.data['file']
        file = pd.read_excel(file)
        file = pd.DataFrame(data = file)
        file.to_dict()
        
        for i in range(0, len(file)):
            Supplier.objects.create(name = file['name'][i], address = file['address'][i], city = file['city'][i], postal_code = file['postal code'][i], country = file['country'][i], bank_name=file['bank name'][i], institution_number = file['institution number'][i], transit_number=file['transit number'][i], bank_account = file['bank account'][i] )
        return Response("Suppliers has been created successfully !!!")


class SuppliersQuestionaryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        try:
            data = request.data
            user = self.request.user
            suppliers = data.get('suppliers')
            categories = data.get('categories')
            if categories:
                c_weight = 0
                for category in categories:
                    c_weight += category.get('weight')
                    if c_weight > 100:
                        return Response(
                            {
                                "success": False,
                                "message": 'Error occurred.',
                                "error": f"Categories weight's more then 100, minus {c_weight - 100}",
                                "data": [],
                            }, status=status.HTTP_400_BAD_REQUEST
                        )
                    q_weight = 0
                    if category.get('questions'):
                        for question in category.get('questions'):
                            q_weight += question.get('weight')
                            if q_weight > category.get('weight'):
                                return Response(
                                    {
                                        "success": False,
                                        "message": 'Error occurred.',
                                        "error": f"Questions weight's more then category weight's, minus {q_weight - category.get('weight')}",
                                        "data": [],
                                    }, status=status.HTTP_400_BAD_REQUEST
                                )

            with transaction.atomic():
                data['creator'] = user.id
                questionary_serializer = SupplierQuestionarySerializer(data=data)
                if not questionary_serializer.is_valid():
                    raise ValidationError(message=f'{make_errors(questionary_serializer.errors)}')
                questionary_serializer.save()
                if suppliers:
                    for supplier in suppliers:
                        supplier['questionary'] = questionary_serializer.data.get('id')
                        supplier_serializers = QuestionarySuppliersSerializers(data=supplier)
                        if not supplier_serializers.is_valid():
                            raise ValidationError(make_errors(supplier_serializers.errors))
                        supplier_serializers.save()
                with transaction.atomic():
                    for category in categories:
                        category['creator'] = user.id
                        category['parent'] = questionary_serializer.data.get('id')
                        category_serializers = SQCategorySerializer(data=category)
                        if not category_serializers.is_valid():
                            raise ValidationError(message=f'{make_errors(category_serializers.errors)}')
                        category_serializers.save()
                        for question in category.get('questions'):
                            question['creator'] = user.id
                            question['parent'] = category_serializers.data.get('id')
                            sre_question_serializers = SQCQuestionSerializer(data=question)
                            if not sre_question_serializers.is_valid():
                                raise ValidationError(message=f'{make_errors(sre_question_serializers.errors)}')
                            sre_question_serializers.save()
                send_alert_supplier_questionary(self.request, questionary_id=questionary_serializer.data.get('id'))
            return Response(
                {
                    "success": True,
                    "message": 'Supplier questionary created successfully.',
                    "error": [],
                    "data": questionary_serializer.data,
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


class SupplierQuestionaryAnswerView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        try:
            data = request.data
            with transaction.atomic():
                for d in data.get("answers"):
                    supplier = Supplier.objects.get(id=data.get("supplier"))
                    d['supplier'] = supplier.id
                    serializer = QuestionaryAnswerSerializers(data=d)
                    if not serializer.is_valid():
                        raise ValidationError(message=f"{make_errors(serializer.errors)}")
                    serializer.save()
            return Response(
                {
                    "success": True,
                    "message": 'Successfully created answers.',
                    "error": [],
                    "data": [],
                }, status=status.HTTP_201_CREATED
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

    def patch(self, request):
        try:
            data = request.data
            checker = self.request.user.id
            with transaction.atomic():
                for d in data:
                    d['checker'] = checker
                    answer = SupplierQuestionaryAnswer.objects.get(id=d.get('id'))
                    serializer = QuestionaryCheckSerializers(answer, data=d, partial=True)
                    if not serializer.is_valid():
                        raise ValidationError(message=f"{make_errors(serializer.errors)}")
                    total_result, create = SupplierQuestionaryResult.objects.get_or_create(
                        checker_id=checker,
                        questionary_id=answer.question.parent.parent.id,
                        supplier_id=answer.supplier.id
                    )
                    total_result.total_weight+=d.get('weight')
                    total_result.save()
                    serializer.save()

                if total_result.questionary.weight > total_result.total_weight:
                    total_result.questionary_status = 'rejected'
                    total_result.save()
                else:
                    total_result.questionary_status = 'congratulations'
                    total_result.save()
                send_result_notification(total_result)

        except ValidationError as e:
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
                "message": 'Successfully checked answers.',
                "error": [],
                "data": [],
            }, status=status.HTTP_200_OK
        )

    # def get(self, request):
    #     try:
    #         user = self.request.user
    #         supplier_id = self.request.data.get('supplier')
    #         supplier = Supplier.objects.select_related('organization', 'create_by', 'supplier', 'parent').filter(
    #             id=supplier_id, organization_id=user.organization.id,
    #         ).first()
    #         questionary_id = self.request.query_params.get('questionary')
    #         questionary = SourcingRequestEvent.objects.select_related('sourcing_request', 'creator', 'parent').filter(
    #             id=questionary_id, general_status='questionary'
    #         ).first()
    #         supplier_answer = SupplierAnswer.objects.select_related('supplier', 'question', 'checker').filter(
    #             supplier_id=supplier.id, question__parent__parent_id=questionary.id
    #         )
    #         # data = questionary.annotate(categories=)
    #     except Exception as e:
    #         return Response(
    #             {
    #                 "success": False,
    #                 "message": 'Error occurred.',
    #                 "error": str(e),
    #                 "data": [],
    #             }, status=status.HTTP_400_BAD_REQUEST
    #         )


class SupplierStatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector)

    def get(self, request):
        try:
            user = self.request.user
            suppliers = Supplier.objects.select_related('organization', 'create_by', 'supplier', 'parent').filter(
                organization_id=user.organization.id
            )
            data = {
                'total': suppliers.count(),
                'active': suppliers.filter(supplier_status='active').count(),
                'inactive': suppliers.filter(supplier_status='inactive').count(),
            }
            return Response(
                {
                    "success": True,
                    "message": 'Successfully got suppliers statistic\'s.',
                    "error": [],
                    "data": data,
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


class GetContractsBySupplierID(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSupplier)

    def get(self, request):
        try:
            user = self.request.user
            contracts = Contract.objects.select_related(
                'parent_agreement', 'departement', 'category', 'currency', 'organization', 'create_by', 'supplier'
            ).filter(supplier__parent_supplier_id=user.id)
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(make_pagination(self.request, ContractGetSerializer, contracts), status=status.HTTP_200_OK)


class SourcingEventBySupplierID(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSupplier)

    def get_queryset(self):
        queryset = SourcingRequestEvent.objects.select_related(
            'sourcing_request', 'creator', 'parent'
        ).filter(sourcing_request_event__supplier__parent_supplier_id=self.request.user.id)
        return queryset

    def get_filter(self):
        queryset = self.get_queryset()
        params = self.request.query_params
        timeline = params.get('timeline')
        event_status = params.get('event_status')
        from_deadline = params.get('from_deadline')
        to_deadline = params.get('to_deadline')

        if timeline:
            queryset = queryset.filter(sourcing_request_event__supplier_timeline__in=timeline.split(','))
        if event_status:
            queryset = queryset.filter(sourcing_event__in=event_status.split(','))
        if from_deadline and not to_deadline:
            queryset = queryset.filter(sourcing_request__deadline_at__gte=from_deadline)
        if from_deadline and to_deadline:
            queryset = queryset.filter(
                sourcing_request__deadline_at__gte=from_deadline,
                sourcing_request__deadline_at__lte=to_deadline
            )
        filtered_events = []
        if queryset is not None:
            supplier_timelines = SourcingRequestEventSuppliers.objects.select_related(
                'supplier', 'sourcingRequestEvent'
            ).filter(supplier__parent_supplier_id=self.request.user.id)
            for event in queryset:
                supplier_current_event_timeline = supplier_timelines.filter(sourcingRequestEvent_id=event.id).first()
                supplier_event = {
                    'id': event.id,
                    'creator': {
                        'id': event.creator.id,
                        'first_name': event.creator.first_name,
                        'last_name': event.creator.last_name,
                    },
                    'title': event.title,
                    'text': event.text,
                    'event_status': event.sourcing_event,
                    'deadline_at': event.get_deadline_at,
                    'supplier_timeline': supplier_current_event_timeline.supplier_timeline
                }
                filtered_events.append(supplier_event)
        return filtered_events

    def get(self, request):
        try:
            data = self.get_filter()
            paginator = LimitOffsetPagination()
            result_page = paginator.paginate_queryset(data, request)
            paginator_response = paginator.get_paginated_response(result_page).data
        except Exception as e:
            return Response(exception_response(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {
                    "success": True,
                    "message": "Successfully got list",
                    "error": [],
                    "count": paginator_response["count"],
                    "next": paginator_response["next"],
                    "previous": paginator_response["previous"],
                    "data": result_page,
                },
            )
