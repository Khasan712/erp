from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
# from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from .models import Supplier


def generate_account_number():
    """ Generate account number """
    suppliers_qty = Supplier.objects.select_related('organization', 'create_by', 'supplier', 'parent').count()
    return f'SP - {suppliers_qty + 1}'


def validate_instance(instance):
    """
     This function validates if instance's supplier is not None or None
     if not None, validate supplier role should be equal to 'supplier' and also instance's parent_supplier field
     should be the same with supplier. If instance's supplier None, instance's parent_supplier
     should be the same with instance's parent -> parent_supplier.
    """

    if instance.supplier is not None:
        if instance.supplier.role != 'supplier':
            raise ValidationError('Only suppliers can assign.')
        instance.parent_supplier = instance.supplier
    elif instance.parent is not None:
        if instance.same_billing_address:
            instance.billing_address = instance.parent.billing_address
        instance.supplier = None
        instance.parent_supplier = instance.parent.parent_supplier
    return instance


@receiver(post_save, sender=Supplier)
def supplier_signals(sender, instance, created, **kwargs):
    """ Generate account function works when supplier created. """

    if created:
        instance.account = generate_account_number()
        instance = validate_instance(instance)
        instance.save()
    # if not created:
    #     instance = validate_instance(instance)
    #     instance.save()
