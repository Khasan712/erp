from rest_framework import serializers
from api.v1.services.models import (
    Service,
    Commodity,
    Consultant,
    ServiceCommodity,
    DocumentService, ServiceCommodityConsultantPrice
)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'frequency', 'must_increase', 'increasePayTerms', 'growthPercentage',
                  'how_many_times')


class ServiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            'id', 'name', 'description', 'frequency', 'must_increase', 'increasePayTerms', 'growthPercentage',
            'get_price', 'get_commodities', 'get_documents')


class CommodityPostSerializers(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ('id', 'name', 'description', 'must_increase', 'growthPercentage', 'increasePayTerms', 'frequency',
                  'how_many_times')


class CommodityListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ('id', 'name', 'description', 'get_price', 'must_increase', 'growthPercentage', 'increasePayTerms',
                  'frequency', 'get_documents')


class ServiceCommodityPostSerializers(serializers.ModelSerializer):
    class Meta:
        model = ServiceCommodity
        fields = ('commodity',)


class CommodityDocumentPostListSerializers(serializers.ModelSerializer):
    class Meta:
        model = DocumentService
        fields = ('id', 'document')


class ConsultantPostListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Consultant
        fields = ('id', 'f_n', 'l_n', 'email', 'c_start_d', 'c_end_d', 'paymentFor', 'must_increase', 'increasePayTerms',
                  'growthPercentage', 'frequency', 'how_many_times')


class ServiceCommodityConsultantPricePostSerializers(serializers.ModelSerializer):
    class Meta:
        model = ServiceCommodityConsultantPrice
        fields = ('id', 'price')













