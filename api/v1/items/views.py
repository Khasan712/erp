from .serializers import ItemSerializer
from .models import Item
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated



class ItemListView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Item.objects.filter(organization = request.user.organization)
        serializer = ItemSerializer(queryset, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def post(self, request):
        serializer = ItemSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(organization = request.user.organization, created_by = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemDetailView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        queryset = Item.objects.filter(organization = request.user.organization).get(id=id)
        serializer = ItemSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        queryset = Item.objects.filter(organization = request.user.organization).get(id=id)
        serializer = ItemSerializer(queryset, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.data, status = status.HTTP_304_NOT_MODIFIED)

    def delete(self, request, id):
        queryset = Item.objects.filter(organization = request.user.organization).get(id=id)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Create your views here.
