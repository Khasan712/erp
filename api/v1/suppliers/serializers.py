from rest_framework import serializers
from api.v1.suppliers.models import (
    Supplier,
    SupplierQuestionary,
    QuestionarySuppliers,
    SupplierQuestionaryAnswer,
)


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'name', 'address', 'city', 'postal_code', 'country', 'bank_name',
                  'institution_number', 'transit_number', 'bank_account', 'supplier', 'parent',
                  "billing_address", "same_billing_address")

    def create(self, validated_data):
        print(validated_data)
        obj = Supplier.objects.create(**validated_data)
        if obj.supplier is not None:
            obj.parent_supplier = validated_data.get('supplier')
        if obj.parent is not None:
            obj.parent_supplier = validated_data.get('parent').parent_supplier
        obj.save()
        return obj


class SupplierGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'supplier', 'name', 'account', 'supplier_status', 'country')

    def to_representation(self, instance):
        response = super(SupplierGetSerializer, self).to_representation(instance)
        response['supplier'] = {
            'first_name': instance.parent_supplier.first_name,
            'last_name': instance.parent_supplier.last_name,
        }
        return response


class SupplierDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = (
            'id', 'supplier', 'name', 'account', 'address', 'city', 'postal_code', 'country', 'supplier_status',
            'bank_name', 'transit_number', 'institution_number', 'bank_account', 'parent', 'get_children',
            'billing_address', 'same_billing_address'
        )

    def to_representation(self, instance):
        response = super(SupplierDetailSerializers, self).to_representation(instance)
        response['supplier'] = {
            'id': instance.parent_supplier.id,
            'first_name': instance.parent_supplier.first_name,
            'last_name': instance.parent_supplier.last_name,
        }
        if response.get('parent') is not None:
            response['parent'] = {
                'id': instance.parent.id,
                'name': instance.parent.name,
                'account': instance.parent.account
            }
        return response

    def update(self, instance, validated_data):
        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.parent_supplier = validated_data.get('parent_supplier', instance.parent_supplier)
        instance.name = validated_data.get('name', instance.name)
        instance.account = validated_data.get('account', instance.account)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.country = validated_data.get('country', instance.country)
        instance.supplier_status = validated_data.get('supplier_status', instance.supplier_status)
        instance.billing_address = validated_data.get('billing_address', instance.billing_address)
        instance.same_billing_address = validated_data.get('same_billing_address', instance.same_billing_address)
        instance.bank_name = validated_data.get('bank_name', instance.bank_name)
        instance.transit_number = validated_data.get('transit_number', instance.transit_number)
        instance.institution_number = validated_data.get('institution_number', instance.institution_number)
        instance.bank_account = validated_data.get('bank_account', instance.bank_account)
        instance.parent = validated_data.get('parent', instance.parent)
        if validated_data.get('parent') is not None:
            instance.supplier = None
            instance.parent_supplier = validated_data.get('parent').parent_supplier
        else:
            if instance.supplier is None:
                return serializers.ValidationError('Select supplier.')
            instance.parent = None
            instance.parent_supplier = instance.supplier
        instance.save()
        return instance


class SupplierMasCreateSerializer(serializers.Serializer):
    file = serializers.FileField()


class SupplierQuestionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierQuestionary
        fields = ('id', 'creator', 'title', 'text', 'weight')

    def create(self, validated_data):
        questionary = SupplierQuestionary(**validated_data)
        questionary.general_status = 'questionary'
        questionary.save()
        return questionary


class SQCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierQuestionary
        fields = ('id', 'creator', 'title', 'text', 'weight', 'parent')

    def create(self, validated_data):
        questionary = SupplierQuestionary(**validated_data)
        questionary.general_status = 'category'
        questionary.save()
        return questionary


class SQCQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierQuestionary
        fields = ('id', 'creator', 'title', 'text', 'weight', 'parent')

    def create(self, validated_data):
        questionary = SupplierQuestionary(**validated_data)
        questionary.general_status = 'question'
        questionary.save()
        return questionary


class QuestionarySuppliersSerializers(serializers.ModelSerializer):
    class Meta:
        model = QuestionarySuppliers
        fields = ('id', 'questionary', 'supplier')


class QuestionaryAnswerSerializers(serializers.ModelSerializer):
    class Meta:
        model = SupplierQuestionaryAnswer
        fields = ('id', 'supplier', 'question', 'answer', 'yes_no')


class QuestionaryCheckSerializers(serializers.ModelSerializer):
    class Meta:
        model = SupplierQuestionaryAnswer
        fields = ('id', 'checker', 'is_true', 'checker_message', 'weight')


