from rest_framework import serializers
from api.v1.contracts.models import Currency, Contract_Type, Cost_Center, Departement, ContractService, ContractCommodity, \
    ContractConsultant
from api.v1.contracts.models import (
    Contract,
    Category,
    ContractTask,
    DocumentContact
)


class ContractFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ('id', 'document')


class ContractListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = (
            'id', 'name', 'contract_number', 'status', 'contract_amount', 'currency', 'contract_structure'
        )

    def to_representation(self, instance):
        response = super(ContractListSerializers, self).to_representation(instance)
        if response.get('currency'):
            response['currency'] = instance.currency.name
        return response


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = (
            'id', 'category_manager', 'contract_owner', 'lawyer', 'project_owner', 'effective_date', 'expiration_date',
            "duration", 'name', 'description', 'parent_agreement', 'departement', 'contract_structure',
            'contract_amount', 'category', 'currency', 'terms', 'status', 'contract_notice', 'notification', 'supplier',
            'serviceCommodityConsultant'
        )

    def validate(self, data):
        if data.get('effective_date') and data.get('expiration_data'):
            if data['effective_date'] < data['expiration_data']:
                raise serializers.ValidationError(
                    'The effective date must be earlier than expiration date, please enter a right date'
                )
        return data

    def to_representation(self, instance):
        response = super(ContractSerializer, self).to_representation(instance)
        if response.get('category_manager'):
            response['category_manager'] = {
                'id': instance.category_manager.id,
                'first_name': instance.category_manager.first_name,
                'last_name': instance.category_manager.last_name,
            }
        if response.get('contract_owner'):
            response['contract_owner'] = {
                'id': instance.contract_owner.id,
                'first_name': instance.contract_owner.first_name,
                'last_name': instance.contract_owner.last_name,
            }
        if response.get('lawyer'):
            response['lawyer'] = {
                'id': instance.lawyer.id,
                'first_name': instance.lawyer.first_name,
                'last_name': instance.lawyer.last_name,
            }
        if response.get('project_owner'):
            response['project_owner'] = {
                'id': instance.project_owner.id,
                'first_name': instance.project_owner.first_name,
                'last_name': instance.project_owner.last_name,
            }
        if response.get('parent_agreement'):
            response['parent_agreement'] = {
                'id': instance.parent_agreement.id,
                'name': instance.parent_agreement.name,
                'contract_number': instance.parent_agreement.contract_number,
            }
        if response.get('departement'):
            response['departement'] = {
                'id': instance.departement.id,
                'name': instance.departement.name,
            }
        if response.get('category'):
            response['category'] = {
                'id': instance.category.id,
                'name': instance.category.name,
            }
        if response.get('currency'):
            response['currency'] = {
                'id': instance.currency.id,
                'name': instance.currency.name,
            }
        if response.get('create_by'):
            response['create_by'] = {
                'id': instance.create_by.id,
                'first_name': instance.create_by.first_name,
                'last_name': instance.create_by.last_name,
            }
        if response.get('supplier'):
            response['supplier'] = instance.supplier.name
        return response


class ContractGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = (
            'id',
            'category_manager',
            'contract_owner',
            'lawyer',
            'project_owner',
            'effective_date',
            'expiration_date',
            "duration",
            'name',
            'contract_number',
            'description',
            'parent_agreement',
            'departement',
            'contract_structure',
            'contract_amount',
            'category',
            'currency',
            'terms',
            'contract_notice',
            'amendment',
            'status',
            'count_changes',
            'notification',
            'supplier',
            'serviceCommodityConsultant',
            'get_agreements',
            'get_service_commodity_consultant',
            'get_tasks',
            'get_documents',
            'get_services'
        )

    def to_representation(self, instance):
        response = super(ContractGetSerializer, self).to_representation(instance)
        if response.get('category_manager'):
            response['category_manager'] = {
                'id': instance.category_manager.id,
                'first_name': instance.category_manager.first_name,
            }
        if response.get('contract_owner'):
            response['contract_owner'] = {
                'id': instance.contract_owner.id,
                'first_name': instance.contract_owner.first_name,
            }
        if response.get('lawyer'):
            response['lawyer'] = {
                'id': instance.lawyer.id,
                'first_name': instance.lawyer.first_name,
            }
        if response.get('project_owner'):
            response['project_owner'] = {
                'id': instance.project_owner.id,
                'first_name': instance.project_owner.first_name,
            }
        if response.get('parent_agreement'):
            response['parent_agreement'] = {
                'id': instance.parent_agreement.id,
                'name': instance.parent_agreement.name,
                'contract_number': instance.parent_agreement.contract_number,
            }
        if response.get('departement'):
            response['departement'] = instance.departement.name
        if response.get('category'):
            response['category'] = instance.category.name
        if response.get('currency'):
            response['currency'] = instance.currency.name
        if response.get('create_by'):
            response['create_by'] = {
                'id': instance.create_by.id,
                'first_name': instance.create_by.first_name,
            }
        if response.get('supplier'):
            response['supplier'] = instance.supplier.name
        return response


class ContractTaskSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContractTask
        fields = ('id', 'contract', 'name', 'is_done')


class DocumentContactSerializers(serializers.ModelSerializer):
    class Meta:
        model = DocumentContact
        fields = ('id', 'contract', 'is_signing', 'document')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'name')


class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract_Type
        fields = ('id','name')


class CostCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cost_Center
        fields = ('id','num', 'name')


class DepartementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = ('id', 'name')


class MassUploadSerializer(serializers.Serializer):
    
    file = serializers.FileField()


class ContractServiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContractService
        fields = ('id', 'service')


class ContractCommoditySerializers(serializers.ModelSerializer):
    class Meta:
        model = ContractCommodity
        fields = ('id', 'commodity')


class ContractConsultantSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContractConsultant
        fields = ('id', 'consultant')

    