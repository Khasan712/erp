from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from api.v1.commons.pagination import make_pagination
from api.v1.commons.views import (
    get_serializer_errors,
    not_serializer_is_valid,
    serializer_valid_response,
    exception_response,
    object_not_found_response,
    object_deleted_response,
    get_serializer_valid_response, return_serializer_errors
)
from api.v1.services.serializers import (
    ServiceSerializer, ServiceCommodityPostSerializers, CommodityPostSerializers,
    CommodityDocumentPostListSerializers, CommodityListSerializers,
    ConsultantPostListSerializers, ServiceListSerializer,
    ServiceCommodityConsultantPricePostSerializers,
)
from api.v1.services.models import (
    Service,
    Commodity,
    Consultant, DocumentService, ServiceCommodity,
)
from api.v1.services.tasks import (
    create_first_increase_terms,
    check_organization_service_commodity_consultant_status
)
from api.v1.users.permissions import IsSourcingDirector, IsContractAdministrator, IsCategoryManager, \
    IsSourcingAdministrator
from api.v1.users.services import make_errors
from django.core.exceptions import ValidationError


class ServicePostListAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated, IsSourcingDirector | IsContractAdministrator | IsCategoryManager |
        IsSourcingAdministrator
    )

    def get_queryset(self):
        queryset = Service.objects.select_related('organization', 'creator').filter(
            organization_id=self.request.user.organization.pk)
        return queryset

    def post(self, request):
        try:
            service_request = self.request.data
            commodities = service_request.get('items')
            user = self.request.user
            service_price = service_request.get('price')
            with transaction.atomic():
                serializer = ServiceSerializer(data=service_request)
                if not serializer.is_valid():
                    raise ValidationError(message=f'{make_errors(serializer.errors)}')
                serializer.save(organization_id=self.request.user.organization.id, creator_id=self.request.user.id)
                if commodities:
                    for commodity in commodities:
                        commodity_serializer = ServiceCommodityPostSerializers(data=commodity)
                        if not commodity_serializer.is_valid():
                            raise ValidationError(message=f'{make_errors(commodity_serializer.errors)}')
                        commodity_serializer.save(service_id=serializer.data.get('id'))
                if service_price is not None:
                    service_price_serializer = ServiceCommodityConsultantPricePostSerializers(
                        data={'price': service_price}
                    )
                    if not service_price_serializer.is_valid():
                        raise ValidationError(message=f'{make_errors(service_price_serializer.errors)}')
                    service_price_serializer.save(
                        organization_id=user.organization.id, forService_id=serializer.data.get('id')
                    )
                if serializer.data.get('must_increase'):
                    if service_price is None:
                        raise ValidationError(message='Please enter service price!')
                    create_first_increase_terms(
                        organization_id=user.organization.id,
                        pk=serializer.data.get('id'),
                        current_price_id=service_price_serializer.data.get('id'),
                        current_price=service_price_serializer.data.get('price'),
                        percentage=serializer.data.get('growthPercentage'),
                        terms=serializer.data.get('increasePayTerms'),
                        how_many_times=serializer.data.get('how_many_times'),
                        section='service'
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
        return Response(
            {
                "success": True,
                "message": 'Service created successfully.',
                "error": [],
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED
        )

    def get(self, request):
        try:
            serializer = ServiceListSerializer
            return Response(
                make_pagination(request, serializer, self.get_queryset()),
                status=status.HTTP_200_OK
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


class ServiceDetailAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated, IsSourcingDirector | IsContractAdministrator | IsCategoryManager |
        IsSourcingAdministrator
    )

    def get_queryset(self):
        queryset = Service.objects.select_related('organization', 'creator').filter(
            organization_id=self.request.user.organization.pk)
        return queryset

    def get_object(self):
        params = self.request.query_params
        service_id = params.get('service')
        return self.get_queryset().filter(id=service_id).first()

    def get_commodity(self, commodity: int):
        commodity = Commodity.objects.select_related('organization', 'creator').filter(id=commodity).last()
        return commodity

    def create_price(self, organization: int, service: int, price: int):
        price_serializer = ServiceCommodityConsultantPricePostSerializers(data={'price': price})
        if not price_serializer.is_valid():
            # raise ValidationError(message=f'{make_errors(price_serializer.errors)}')
            return price_serializer
        price_serializer.save(organization_id=organization, forService_id=service)
        return True

    def get(self, request):
        try:
            if not self.get_object():
                return Response(
                    object_not_found_response(), status=status.HTTP_204_NO_CONTENT
                )
            serializer = ServiceListSerializer(self.get_object())
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

    def patch(self, request):
        try:
            if not self.get_object():
                return Response(
                    object_not_found_response(), status=status.HTTP_204_NO_CONTENT
                )
            service_request = self.request.data
            commodities = service_request.get('items')
            price = service_request.get('price')
            with transaction.atomic():
                serializer = ServiceSerializer(self.get_object(), data=service_request, partial=True)
                if not serializer.is_valid():
                    raise ValidationError(message=f'{make_errors(serializer.errors)}')
                serializer.save()
                if price:
                    create_price = self.create_price(
                        organization=self.get_object().organization.id, service=self.get_object().id, price=price)
                    if not create_price == True:
                        raise ValidationError(message=f'{create_price.errors}')
                if commodities:
                    for service_commodity in commodities:
                        commodity = self.get_commodity(commodity=service_commodity.get('commodity'))
                        if not commodity:
                            raise ValidationError(message=f"Commodity not found, ID {service_commodity.get('commodity')}")
                        service_commodity_item = ServiceCommodity.objects.get(
                            commodity_id=commodity.id, service_id=self.get_object().id)
                        service_commodity_serializer = ServiceCommodityPostSerializers(
                            service_commodity_item, data=service_commodity, partial=True)
                        if not service_commodity_serializer.is_valid():
                            raise ValidationError(message=f'{make_errors(service_commodity_serializer.errors)}')
                        service_commodity_serializer.save()
            return Response(
                {
                    "success": True,
                    "message": 'Service has successfully updated.',
                    "error": [],
                    "data": serializer.data,
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

    def delete(self, request):
        try:
            if not self.get_object():
                return Response(
                    object_not_found_response(), status=status.HTTP_204_NO_CONTENT
                )
            service = self.get_object()
            service.delete()
            return Response(
                {
                    "success": True,
                    "message": 'Service has successfully deleted.',
                    "error": [],
                    "data": [],
                }, status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )


class CommodityPostListAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated, IsSourcingDirector | IsContractAdministrator | IsCategoryManager |
        IsSourcingAdministrator
    )

    def get_queryset(self):
        queryset = Commodity.objects.select_related('organization', 'creator').filter(
            organization_id=self.request.user.organization.pk)
        return queryset

    def post(self, request):
        try:
            commodity_request = self.request.data
            user = self.request.user
            documents = commodity_request.get('documents')
            commodity_price = commodity_request.get('price')
            with transaction.atomic():
                serializer = CommodityPostSerializers(data=self.request.data)
                if not serializer.is_valid():
                    raise ValidationError(message=f'{make_errors(serializer.errors)}')
                serializer.save(organization_id=self.request.user.organization.pk, creator_id=self.request.user.pk)
                if documents:
                    for document in documents:
                        document_serializer = CommodityDocumentPostListSerializers(data=document)
                        if not document_serializer.is_valid():
                            get_serializer_errors(document_serializer)
                        document_serializer.save(commodity_id=serializer.data.get('id'))

                if commodity_price is not None:
                    commodity_price_serializer = ServiceCommodityConsultantPricePostSerializers(data={'price': commodity_price})
                    if not commodity_price_serializer.is_valid():
                        raise ValidationError(message=f'{make_errors(commodity_price_serializer.errors)}')
                    commodity_price_serializer.save(organization_id=user.organization.id, forCommodity_id=serializer.data.get('id'))
                if serializer.data.get('must_increase'):
                    if commodity_price is None:
                        raise ValidationError(message='Please enter service price!')
                    create_first_increase_terms(
                        organization_id=user.organization.id,
                        pk=serializer.data.get('id'),
                        current_price_id=commodity_price_serializer.data.get('id'),
                        current_price=commodity_price_serializer.data.get('price'),
                        percentage=serializer.data.get('growthPercentage'),
                        terms=serializer.data.get('increasePayTerms'),
                        how_many_times=serializer.data.get('how_many_times'),
                        section='commodity'
                    )

            return Response(
                {
                    "success": True,
                    "message": 'Commodity created successfully.',
                    "error": [],
                    "data": serializer.data,
                }, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request):
        try:
            serializer = CommodityListSerializers
            return Response(
                make_pagination(request, serializer, self.get_queryset()),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )


class CommodityDetailAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated, IsSourcingDirector | IsCategoryManager | IsSourcingAdministrator
    )

    def get_queryset(self):
        queryset = Commodity.objects.select_related('organization', 'creator').filter(
            organization_id=self.request.user.organization.pk)
        return queryset

    def get_object(self):
        params = self.request.query_params
        commodity_id = params.get('commodity')
        return self.get_queryset().filter(id=commodity_id).first()

    def create_price(self, organization: int, commodity: int, price: int):
        price_serializer = ServiceCommodityConsultantPricePostSerializers(data={'price': price})
        if not price_serializer.is_valid():
            return price_serializer
        price_serializer.save(organization_id=organization, forCommodity_id=commodity)
        return True

    def get(self, request):
        try:
            if not self.get_object():
                return Response(
                    object_not_found_response(), status=status.HTTP_204_NO_CONTENT
                )
            serializer = CommodityListSerializers(self.get_object())
            return Response(
                {
                    "success": True,
                    "message": 'Commodity got successfully.',
                    "error": [],
                    "data": serializer.data,
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

    def patch(self, request):
        try:
            commodity_request = self.request.data
            documents = commodity_request.get('get_documents')
            price = commodity_request.get('price')
            if not self.get_object():
                return Response(
                    object_not_found_response(), status=status.HTTP_204_NO_CONTENT
                )
            with transaction.atomic():
                serializer = CommodityListSerializers(self.get_object(), data=commodity_request, partial=True)
                if not serializer.is_valid():
                    get_serializer_errors(serializer)
                serializer.save()
                if documents:
                    for document_request in documents:
                        document = DocumentService.objects.select_related('service', 'commodity').get(
                            id=document_request.get('id'))
                        document_serializer = CommodityDocumentPostListSerializers(document, data=document_request, partial=True)
                        if not document_serializer.is_valid():
                            get_serializer_errors(serializer)
                        document_serializer.save()
                if price:
                    create_price = self.create_price(
                        organization=self.get_object().organization.id, commodity=self.get_object().id, price=price)
                    if not create_price == True:
                        raise ValidationError(message=f'{create_price.errors}')
            return Response(
                {
                    "success": True,
                    "message": 'Commodity has successfully updated.',
                    "error": [],
                    "data": serializer.data,
                }, status=status.HTTP_400_BAD_REQUEST
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

    def delete(self, request):
        try:
            if not self.get_object():
                return Response(
                    object_not_found_response(), status=status.HTTP_204_NO_CONTENT
                )
            commodity = self.get_object()
            commodity.delete()
            return Response(
                {
                    "success": True,
                    "message": 'Commodity has successfully deleted.',
                    "error": [],
                    "data": [],
                }, status=status.HTTP_204_NO_CONTENT
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


class ConsultantPostListAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated, IsSourcingDirector | IsContractAdministrator | IsCategoryManager |
        IsSourcingAdministrator
    )

    def get_queryset(self):
        queryset = Consultant.objects.select_related('organization', 'creator').filter(
            organization_id=self.request.user.organization.pk)
        return queryset

    def post(self, request):
        try:
            consultant_request = self.request.data
            user = self.request.user
            consultant_price = consultant_request.get('price')
            with transaction.atomic():
                serializer = ConsultantPostListSerializers(data=consultant_request)
                if not serializer.is_valid():
                    raise ValidationError(return_serializer_errors(serializer))
                serializer.save(organization_id=self.request.user.organization.pk, creator_id=self.request.user.pk)
                if consultant_price:
                    consultant_price_serializer = ServiceCommodityConsultantPricePostSerializers(
                        data={'price': consultant_price})
                    if not consultant_price_serializer.is_valid():
                        raise ValidationError(message=f'{make_errors(consultant_price_serializer.errors)}')
                    consultant_price_serializer.save(organization_id=user.organization.id,
                                                     forConsultant_id=serializer.data.get('id'))

                if serializer.data.get('must_increase'):
                    if consultant_price is None:
                        raise ValidationError(message='Please enter Consultant price!')
                    create_first_increase_terms(
                        organization_id=user.organization.id,
                        pk=serializer.data.get('id'),
                        current_price_id=consultant_price_serializer.data.get('id'),
                        current_price=consultant_price_serializer.data.get('price'),
                        percentage=serializer.data.get('growthPercentage'),
                        terms=serializer.data.get('increasePayTerms'),
                        how_many_times=serializer.data.get('how_many_times'),
                        section='consultant'
                    )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer_valid_response(serializer), status=status.HTTP_201_CREATED
        )

    def get(self, request):
        try:
            serializer = ConsultantPostListSerializers
            return Response(
                make_pagination(request, serializer, self.get_queryset()),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )


class ConsultantDetailAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated, IsSourcingDirector | IsCategoryManager | IsSourcingAdministrator
    )

    def get_queryset(self):
        queryset = Consultant.objects.select_related('organization', 'creator').filter(
            organization_id=self.request.user.organization.pk)
        return queryset

    def get_object(self):
        params = self.request.query_params
        service_id = params.get('consultant')
        return self.get_queryset().filter(id=service_id).first()

    def create_price(self, organization: int, consultant: int, price: int):
        price_serializer = ServiceCommodityConsultantPricePostSerializers(data={'price': price})
        if not price_serializer.is_valid():
            return price_serializer
        price_serializer.save(organization_id=organization, forConsultant_id=consultant)
        return True

    def get(self, request):
        try:
            if not self.get_object():
                return Response(
                    object_not_found_response(), status=status.HTTP_204_NO_CONTENT
                )
            serializer = ConsultantPostListSerializers(self.get_object())
            return Response(
                get_serializer_valid_response(serializer), status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request):
        try:
            consultant_request = self.request.data
            price = consultant_request.get('price')
            if not self.get_object():
                return Response(
                    object_not_found_response(), status=status.HTTP_204_NO_CONTENT
                )
            with transaction.atomic():
                serializer = ConsultantPostListSerializers(self.get_object(), data=consultant_request, partial=True)
                if not serializer.is_valid():
                    get_serializer_errors(serializer)
                serializer.save()
                if price:
                    create_price = self.create_price(
                        organization=self.get_object().organization.id, consultant=self.get_object().id, price=price)
                    if not create_price == True:
                        raise ValidationError(message=f'{create_price.errors}')
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer_valid_response(serializer), status=status.HTTP_200_OK
        )

    def delete(self, request):
        try:
            if not self.get_object():
                return Response(
                    object_not_found_response(), status=status.HTTP_204_NO_CONTENT
                )
            consultant = self.get_object()
            consultant.delete()
            return Response(
                object_deleted_response(), status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                exception_response(e), status=status.HTTP_400_BAD_REQUEST
            )


# class ServiceListView(APIView):

#     def get(self, request):
#         queryset = Service.objects.filter(org = request.user.organization)
#         serializer = ServiceSerializer(queryset)
#         return Response(serializer.data, status = status.HTTP_200_OK)

#     def post(self, request):
#         serializer = ServiceSerializer(data = request.data)
#         if serializer.is_valid():
#             serializer.save(organization = request.user.organization, created_by = request.user)
#             return Response(serializer.data, status = status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class SerciceDetailView(APIView):

#     def get(self, request, id):
#         queryset = Service.objects.filter(organization = request.user.organization).get(id=id)
#         serializer = ServiceSerializer(queryset)
#         return Response(serializer.data, status = status.HTTP_200_OK)

#     def put(self, request, id):
#         queryset = Service.objects.filter(organization = request.user.organization).get(id=id)
#         serializer = Service(queryset, data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request,id):
#         queryset = Service.objects.filter(organization = request.user.organization).get(id=id)
#         queryset.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class CheckServiceStatus(APIView):

    def post(self, request):
        try:
            check_organization_service_commodity_consultant_status()
        except Exception as e:
            return Response(str(e))
        return Response('It is working')

