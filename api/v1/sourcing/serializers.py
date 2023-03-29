from rest_framework import serializers
from .models import (
    CategoryRequest,
    SourcingRequest,
    DocumentSourcing,
    SourcingComments,
    SourcingRequestEvent,
    SourcingRequestEventSuppliers,
    SupplierResult, SourcingRequestService, SourcingRequestCommodity, SourcingRequestConsultant, SourcingRequestAssigned
)
from .models import SupplierAnswer
from api.v1.users.serializers import (
    UserSerializer,
)


class CategoryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryRequest
        fields = ('id', 'name')


class SourcingRequestGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequest
        fields = (
            'id', 'sourcing_request_name', 'categoryRequest', 'currency', 'estimated_budget', 'deadline_at',
            'sourcing_event', 'departement', 'requestor', 'sourcing_number', 'description',
            'sourcing_request_status', 'get_documents', 'created_at', 'serviceCommodityConsultant', 'get_assigned_users'
        )

    def to_representation(self, instance):
        res = super(SourcingRequestGetSerializer, self).to_representation(instance)
        if res.get('categoryRequest'):
            res['categoryRequest'] = {
                'id': instance.categoryRequest.id,
                'name': instance.categoryRequest.name
            }
        if res.get('departement'):
            res['departement'] = {
                'id': instance.departement.id,
                'name': instance.departement.name,
            }
        if res.get('currency'):
            res['currency'] = {
                'id': instance.currency.id,
                'name': instance.currency.name,
            }
        if res.get('requestor'):
            res['requestor'] = {
                'id': instance.requestor.id,
                'f_name': instance.requestor.first_name,
                'l_name': instance.requestor.last_name,
                'role': instance.requestor.role,
            }
        return res


class SourcingRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequest
        fields = (
            'id', 'sourcing_request_name', 'categoryRequest', 'currency', 'estimated_budget', 'deadline_at',
            'sourcing_event', 'sourcing_number', 'sourcing_request_status', 'get_documents'
        )

    def to_representation(self, instance):
        res = super(SourcingRequestListSerializer, self).to_representation(instance)
        if res.get('categoryRequest'):
            res['categoryRequest'] = instance.categoryRequest.name
        if res.get('currency'):
            res['currency'] = instance.currency.name
        return res


class SourcingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequest
        exclude = ('updated_at', 'sourcing_number', 'sourcing_request_status', 'organization', 'assigned_to')


class EventInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'title', 'text', 'creator', 'parent')
    
    def create(self, validated_data):
        sre_info = SourcingRequestEvent(**validated_data)
        sre_info.general_status = 'info'
        sre_info.save()
        return sre_info


class EventInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('title', 'text')

    def create(self, validated_data):
        sre_info = SourcingRequestEvent(**validated_data)
        sre_info.general_status = 'info'
        sre_info.save()
        return sre_info


class EventQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'text', 'weight', 'creator', 'yes_no', 'answer', 'parent')

    def create(self, validated_data):
        sre_question = SourcingRequestEvent(**validated_data)
        sre_question.general_status = 'question'
        sre_question.save()
        return sre_question


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'title', 'text', 'weight', 'creator', 'parent')
    
    def create(self, validated_data):
        sre_category = SourcingRequestEvent(**validated_data)
        sre_category.general_status = 'category'
        sre_category.save()
        return sre_category


class EventQuestionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'title', 'creator', 'success_weight', 'parent')
        
    def create(self, validated_data):
        sre_questionary = SourcingRequestEvent(**validated_data)
        sre_questionary.general_status = 'questionary'
        sre_questionary.save()
        return sre_questionary


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'sourcing_event', 'sourcing_request', 'creator', 'general_status', 'title', 'text')

    def create(self, validated_data):
        sre_event = SourcingRequestEvent(**validated_data)
        sre_event.general_status = 'sourcing_event'
        sre_event.save()
        return sre_event


class EventUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'sourcing_event', 'title', 'text', 'sourcing_request')

    def to_representation(self, instance):
        response = super(EventUpdateSerializer, self).to_representation(instance)
        if response.get('sourcing_request'):
            response['sourcing_request'] = {
                'id': instance.sourcing_request.id,
                'name': instance.sourcing_request.sourcing_request_name
            }
        return response


class GetEventByRequestIDSerializers(serializers.ModelSerializer):
    # creator = serializers.SerializerMethodField(source='first_name')
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'creator', 'sourcing_event', 'title', 'text', 'created_at')

    def to_representation(self, instance):
        response = super(GetEventByRequestIDSerializers, self).to_representation(instance)
        response['creator'] = instance.creator.first_name
        return response


class EventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'sourcing_request', 'sourcing_event', 'creator', 'title', 'text', 'get_questionary_data')


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEventSuppliers
        fields = ('supplier', 'sourcingRequestEvent')


class EventSupplierUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEventSuppliers
        fields = ('supplier',)


class SourcingCommentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = SourcingComments
        fields = ('__all__',)


class SourcingCommentsQuestionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingComments
        fields = ('id', 'supplier', 'text')


class SourcingCommentsQuestionaryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingComments
        fields = ('id', 'supplier', 'text', 'created_date', 'author')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if res.get('supplier'):
            res['supplier'] = {
                'id': instance.supplier.id,
                'name': instance.supplier.name
            }
        if res.get('author'):
            res['author'] = {
                'id': instance.author.id,
                'first_name': instance.author.first_name,
                'last_name': instance.author.last_name
            }
        return res


class SourcingGetCommentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = SourcingComments
        exclude = ('sourcingRequestEvent', 'sourcingRequest')


class SupplierAnswerSerializers(serializers.ModelSerializer):
    class Meta:
        model = SupplierAnswer
        fields = ('question', 'yes_no', 'answer', 'supplier')


class CheckSASerializers(serializers.ModelSerializer):
    """ Checking supplier answer by checker """
    class Meta:
        model = SupplierAnswer
        fields = ('id', 'weight')


class SupplierResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierResult
        fields = ('questionary', 'supplier', 'total_weight', 'questionary_status')


class DocumentSourcingRequestSerializer(serializers.ModelSerializer):
    sourcingFiles = serializers.FileField()
    class Meta:
        model = DocumentSourcing
        fields = ('id', 'sourcingFiles', 'sourcingRequest')


class DocumentSourcingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentSourcing
        fields = ('id', 'sourcingFiles')


class SourcingEventBySourcingRequestIDSerializers(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'creator', 'title', 'text', 'created_at', 'sourcing_event', 'sourcing_request')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response.get('creator'):
            response['creator'] = instance.creator.first_name
        response['sourcing_request'] = {
            'name': instance.sourcing_request.sourcing_request_name,
            'sourcing_number': instance.sourcing_request.sourcing_number
        }
        return response


class SourcingEventSuppliersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEventSuppliers
        fields = ('id', 'supplier', 'supplier_timeline', 'get_total_weight')

    def to_representation(self, instance):
        response = super(SourcingEventSuppliersSerializer, self).to_representation(instance)
        if response.get('supplier'):
            response['supplier'] = {
                'id': instance.supplier.id,
                'name': instance.supplier.name,
                'organization': instance.supplier.organization.name
            }
        return response


class SourcingEventInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'title', 'text')


class SourcingEventQuestionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'title', 'success_weight', 'get_questionary_data')


class SourcingEventSupplierQuestionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'title', 'success_weight')


class SourcingRequestServiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestService
        fields = ('id', 'sourcingService')


class SourcingRequestCommoditySerializers(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestCommodity
        fields = ('id', 'sourcingCommodity')


class SourcingRequestConsultantSerializers(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestConsultant
        fields = ('id', 'sourcingConsultant')


class SourcingRequestAssignedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestAssigned
        fields = ('id', 'assigned')


class GetSupplierSourcingEvents(serializers.ModelSerializer):
    class Meta:
        model = SourcingRequestEvent
        fields = ('id', 'creator', 'title', 'text', 'sourcing_event', 'get_deadline_at')

    def to_representation(self, instance):
        response = super(GetSupplierSourcingEvents, self).to_representation(instance)
        response['creator'] = {
            'id': instance.creator.id,
            'first_name': instance.creator.first_name,
            'last_name': instance.creator.last_name,
        }
        return response


class SupplierAnswerInEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierAnswer
        fields = ('id', 'supplier', 'question', 'answer', 'yes_no', 'checker', 'weight')

    def to_representation(self, instance):
        res = super(SupplierAnswerInEventSerializer, self).to_representation(instance)
        if res.get('supplier'):
            res['supplier'] = {
                'id': instance.supplier.id,
                'name': instance.supplier.name,
            }
        if res.get('question'):
            res['question'] = {
                "id": instance.question.id,
                "title": instance.question.title,
                "text": instance.question.text,
                "answer": instance.question.answer,
                "yes_no": instance.question.yes_no,
                # "category": {
                #     "id":
                # }
            }
        if res.get('checker'):
            res['checker'] = {
                'id': instance.checker.id,
                'first_name': instance.checker.first_name,
                'last_name': instance.checker.last_name,
            }
        return res
