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
        fields = ('id', 'name', 'account', 'address', 'city','postal_code','country', 'bank_name','institution_number','transit_number','bank_account')


class SupplierGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'supplier', 'name', 'account', 'supplier_status', 'country')

    def to_representation(self, instance):
        response = super(SupplierGetSerializer, self).to_representation(instance)
        response['supplier'] = {
            'first_name': instance.supplier.first_name,
            'last_name': instance.supplier.last_name,
        }
        return response


class SupplierDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = (
            'id', 'supplier', 'name', 'account', 'address', 'city', 'postal_code', 'country', 'supplier_status',
            'bank_name', 'transit_number', 'institution_number', 'bank_account', 'parent', 'get_children'
        )

    def to_representation(self, instance):
        response = super(SupplierDetailSerializers, self).to_representation(instance)
        response['supplier'] = {
            'first_name': instance.supplier.first_name,
            'last_name': instance.supplier.last_name,
        }
        if response.get('parent') is not None:
            response['parent'] = {
                'id': instance.parent.id,
                'name': instance.parent.name,
                'account': instance.parent.account
            }
        return response


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


