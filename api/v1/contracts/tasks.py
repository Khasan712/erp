from config.celery import app
from api.v1.users.utils import (
    send_email_for_contract_notice,
    send_email_auto_renew,
    send_email_fixed
)
from .models import (
    ContractNotificationDay,
    Contract,
)
from django.db import transaction
from celery import shared_task
import datetime


@app.task
def send_beat_email():
    contracts = ContractNotificationDay.objects.select_related('contract').filter(
        send_email_day=datetime.datetime.today(), is_send=False)
    with transaction.atomic():
        for contract in contracts:
            send_email_for_contract_notice(contract.contract.category_manager.email)
            contract.is_send = True
            contract.save()


@app.task
def check_fixed_terms():
    fixed_terms = Contract.objects.select_related('parent_agreement', 'departement', 'category', 'currency',
            'organization', 'create_by', 'supplier').filter(
        terms='Fixed', expiration_date=datetime.datetime.today(), is_send_fixed=False)
    with transaction.atomic():
        for contract in fixed_terms:
            contract.status = 'EXPIRED'
            send_email_fixed(contract.category_manager.email, contract.pk)
            contract.is_send_fixed = True
            contract.save()


@app.task
def check_auto_renew_terms():
    auto_renews = Contract.objects.select_related('parent_agreement', 'departement', 'category', 'currency',
            'organization', 'create_by', 'supplier').filter(terms='Auto Renew', expiration_date=datetime.datetime.today())
    with transaction.atomic():
        for contract in auto_renews:
            contract.expiration_date = contract.expiration_date + (contract.expiration_date - contract.effective_date)
            contract.save()
            send_email_auto_renew(contract.category_manager.email, contract.expiration_date, contract.pk)


