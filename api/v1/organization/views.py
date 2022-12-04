from django.shortcuts import render
from rest_framework.response import Response
from api.v1.organization.models import Organization
from api.v1.organization.serializers import OrganizationSerializer
from rest_framework.views import APIView
from rest_framework import status


class OrganizationListView(APIView):
    def get(self, request):
        queryset = Organization.objects.all()
        serializer = OrganizationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OrganizationSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationDetailListView(APIView):

    def get(self, request, id):
        queryset = Organization.objects.get(id=id)
        serializer = OrganizationSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        queryset = Organization.objects.get(id=id)
        serializer = OrganizationSerializer(queryset, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, id):
        queryset = Organization.objects.get(id=id)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Create your views here.
