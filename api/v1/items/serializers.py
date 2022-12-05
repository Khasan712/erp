from rest_framework import serializers
from .models import Item, Category, Storeroom, Department


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class StoreroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storeroom
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only = True, many=True)
    storeroom = StoreroomSerializer(read_only = True, many=True)
    category = CategorySerializer(read_only = True, many=True)
    
    class Meta:
        depth = 1
        model = Item
        fields = ('id','name','description','sku', 'min','max', 'current_balance','supplier','order_unit','issue_unit','price','reorder_qty','picture','status','storeroom', 'department', 'category', 'created_by','organization',)

