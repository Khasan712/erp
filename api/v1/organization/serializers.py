from dataclasses import field
from rest_framework import serializers
from api.v1.organization.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'address', 'postal_code', 'city', 'country')