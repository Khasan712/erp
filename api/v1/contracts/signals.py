from django.db import transaction
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from .history_contract_models import HistoryContract
from .models import (
    Contract,
    ContractNotificationDay,
    ConnectContractWithTask,
    ContractTask
)
import datetime
# from .history_contract_models import HistoryContract
from ..chat.notification_models.notifications import ContractNotification
from ..chat.views import send_to_supplier_from_contract
from ..users.models import User


def create_notify_days(instance):
    if instance.contract_notice and instance.notification:
        # instance.duration = instance.expiration_date - instance.effective_date
        send_email_day = instance.expiration_date - datetime.timedelta(days=instance.contract_notice)
        with transaction.atomic():
            ContractNotificationDay.objects.create(
                contract_id=instance.id, send_email_day=send_email_day
            )
            if instance.notification:
                last_n_day = ContractNotificationDay.objects.filter(contract_id=instance.id).last()
                enterval_days = instance.expiration_date - last_n_day.send_email_day
                for d in range(1, int(enterval_days.days) + 1):
                    if d % instance.notification == 0:
                        if last_n_day.send_email_day + datetime.timedelta(
                                days=instance.notification) <= instance.expiration_date:
                            last_n_day = ContractNotificationDay.objects.filter(contract_id=instance.id).last()
                            new = ContractNotificationDay(
                                contract_id=instance.id,
                                send_email_day=last_n_day.send_email_day + datetime.timedelta(
                                    days=instance.notification)
                            )
                            new.save()


def create_task_for_contract(instance):
    tasks = ContractTask.objects.select_related('organization')
    if tasks:
        with transaction.atomic():
            for task in tasks:
                connecting_with_task = ConnectContractWithTask(
                    contract_id=instance.id,
                    task_id=task.id
                )
                connecting_with_task.save()


def notify_supplier(contract, supplier):
    notify = ContractNotification(
        contract_id=contract,
        receiver_id=supplier.supplier.id
    )
    notify.save()
    send_to_supplier_from_contract(supplier.supplier.email)


def save_contract_history(instance):
    instance_values = instance.__dict__.copy()
    instance_values['contract_id'] = instance_values['id']
    instance_values['contract_amendment'] = instance_values['amendment']
    del instance_values['_state']
    del instance_values['id']
    del instance_values['amendment']
    a = HistoryContract.objects.create(**instance_values)


@receiver(post_save, sender=Contract)
def contract_signals(sender, instance, created, **kwargs):
    if created:
        create_notify_days(instance)
        create_task_for_contract(instance)
        # notify_supplier(instance.id, instance.supplier)
    if not created and instance.status in ('ACTIVE', 'EXPIRED'):
        save_contract_history(instance)

