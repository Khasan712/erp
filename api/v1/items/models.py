from django.db import models
from api.v1.suppliers.models import Supplier
from api.v1.organization.models import Organization
from api.v1.users.models import User


class Category(models.Model):
    name = models.CharField(max_length=75)
    created_by = models.ForeignKey(User, models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='Organization')


choice = (
    ('IN', 'IN'),
    ('OUT', 'OUT'),
    ('CRI', 'CRI')
)


class Storeroom(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    # bill_to = models.CharField(max_length=100) to remove because the bill is supposed to be applied on PO


class Department(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


orderunit = (
    ('FT', 'FT'),
    ('M', 'M'),
    ('PO', 'PO'),
    ('IN', 'IN'),
    ('L', 'L'),
    ('CM', 'CM')
)

issueunit = (
    ('FT', 'FT'),
    ('M', 'M'),
    ('PO', 'PO'),
    ('IN', 'IN'),
    ('L', 'L'),
    ('CM', 'CM')
)


class Item(models.Model):
    creation_date = models.DateField()
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=500, null=True, blank=True)
    sku = models.CharField(max_length=20,null=True, blank=True) # formula to increment after each saving
    storeroom = models.ForeignKey(Storeroom, on_delete=models.CASCADE)
    min = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)
    current_balance = models.FloatField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    supplier = models.ManyToManyField(Supplier, blank=True)
    order_unit = models.CharField(max_length=7, choices=orderunit) # maybe a ForeignKey
    issue_unit = models.CharField(max_length=10, choices=issueunit)
    price = models.FloatField(default=0)
    #location
    #bin
    # supplier_sku = models.CharField(max_length=30)
    reorder_qty  = models.FloatField(blank=True, null=True) 
    # [if current_balance <= min ====> reorder_qty = max - current_balance ]
    picture = models.FileField(blank=True, null=True)
    # type = models.CharField(max_length=50, choice = type)
    status = models.CharField(max_length=20, choices=choice)
    category = models.ForeignKey(Category, on_delete= models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.name}'

    def save(self, *args, **kwargs):
        self.reorder_qty = self.max-self.current_balance
        super(Item, self).save(*args, **kwargs)


# create a model for services and another for asset (asset management)

