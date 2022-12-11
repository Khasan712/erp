from django.db import transaction
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import (
    Contract,
    ContractNotificationDay,
    ConnectContractWithTask,
    ContractTask
)
import datetime
from django.forms import model_to_dict
from .history_contract_models import HistoryContract


@receiver(post_save, sender=Contract)
def create_notification(sender, instance, created, **kwargs):
    if created:
        if instance.contract_notice and instance.notification:
            instance.duration = 
            send_email_day = instance.expiration_date - datetime.timedelta(days=instance.contract_notice)
            with transaction.atomic():
                ContractNotificationDay.objects.create(
                    contract_id=instance.id, send_email_day=send_email_day
                )
                if instance.notification:
                    last_n_day = ContractNotificationDay.objects.filter(contract_id=instance.id).last()
                    enterval_days = instance.expiration_date - last_n_day.send_email_day
                    for d in range(1, int(enterval_days.days)+1):
                        if d % instance.notification == 0:
                            if last_n_day.send_email_day + datetime.timedelta(days=instance.notification) <= instance.expiration_date:
                                last_n_day = ContractNotificationDay.objects.filter(contract_id=instance.id).last()
                                new = ContractNotificationDay(
                                    contract_id=instance.id,
                                    send_email_day=last_n_day.send_email_day + datetime.timedelta(days=instance.notification)
                                )
                                new.save()

    # if not created:
    #     history = ContractHistory(
    #         contract=instance.id,
    #         amendment=instance.amendment,
    #         effective_date=instance.effective_date,
    #         expiration_date=instance.expiration_date,
    #         duration=instance.duration,
    #         name=instance.name,
    #         description=instance.descriptionDescription,
    #         contract_structure=instance.contract_structure,
    #         contract_amount=instance.contract_amount,
    #         category=instance.category,
    #         currency=instance.currency,
    #         terms=instance.terms,
    #         contract_notice=instance.contract_notice,
    #         notification=instance.notification,
    #         supplier=instance.supplier,
    #         departement=instance.departement,
    #         parent_agreement=instance.parent_agreement
    #     )
    #     history.save()


@receiver(post_save, sender=Contract)
def create_task_for_contract(sender, instance, created, **kwargs):
    tasks = ContractTask.objects.select_related('organization')
    if tasks and created:
        with transaction.atomic():
            for task in tasks:
                connecting_with_task = ConnectContractWithTask(
                    contract_id=instance.id,
                    task_id=task.id
                )
                connecting_with_task.save()


# @receiver(post_save, sender=Contract)
# def save_contract_updates(sender, instance, created, **kwargs):
#     if instance.status == 'ACTIVE' or instance.status == 'EXPIRED':
#         contract_fields = model_to_dict(instance)
#         contract_fields['category_manager_id'] = contract_fields['category_manager']
#         del contract_fields['id']
#         del contract_fields['category_manager']
#
#         print(contract_fields)
#
#         history = HistoryContract(
#             in_contract_id=instance.id,
#             **contract_fields
#         )
#         history.save()




#     if created:
#         if instance.status == 'ACTIVE' or instance.status == 'EXPIRED':
#             history = HistoryContract(
#                 contract=instance.id,
#
#                 category_manager=instance.category_manager,
#                 contract_owner=instance.contract_owner,
#                 lawyer=instance.lawyer,
#                 project_owner=instance.project_owner,
#
#                 creation_date=instance.creation_date,
#                 effective_date=instance.effective_date,
#                 expiration_date=instance.expiration_date,
#                 duration=instance.duration,
#
#                 #
#                 # amendment=instance.amendment,
#                 # name=instance.name,
#                 # description=instance.descriptionDescription,
#                 # contract_structure=instance.contract_structure,
#                 # contract_amount=instance.contract_amount,
#                 # category=instance.category,
#                 # currency=instance.currency,
#                 # terms=instance.terms,
#                 # contract_notice=instance.contract_notice,
#                 # notification=instance.notification,
#                 # supplier=instance.supplier,
#                 # departement=instance.departement,
#                 # parent_agreement=instance.parent_agreement
#                 **instance
#             )
#             history.save()
# #



