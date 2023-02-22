from config.celery import app
from api.v1.chat.views import send_email_to_service_creator
from api.v1.contracts.models import ContractService, ContractCommodity, ContractConsultant
from api.v1.organization.models import Organization
from api.v1.users.utils import (
    send_email_for_contract_notice,
    send_email_auto_renew,
    send_email_fixed
)
from .models import (
    Service,
    Commodity,
    Consultant,
    ServiceCommodityConsultantPayTermsIncrease,
    ServiceCommodityConsultantPrice
)
from celery import shared_task
from django.db import transaction
import datetime


def get_increase_date(increase_term, how_many_times):
    print(how_many_times)
    match increase_term:
        case 'weekly':
            return datetime.timedelta(weeks=how_many_times)
        case 'monthly':
            return datetime.timedelta(days=(30 * how_many_times))
        case 'yearly':
            return datetime.timedelta(days=(365 * how_many_times))


def create_new_price(organization, pk, price, section):
    section_price = ServiceCommodityConsultantPrice(
        organization_id=organization,
        price=price
    )
    match section:
        case 'service':
            section_price.forService_id = pk
        case 'commodity':
            section_price.forCommodity_id = pk
        case 'consultant':
            section_price.forConsultant_id = pk
    section_price.save()
    return section_price


@app.task
def create_first_increase_terms(
        organization_id, pk, current_price_id, current_price, percentage, terms, how_many_times, section,
):
    service_term = ServiceCommodityConsultantPayTermsIncrease(
        organization_id=organization_id,
        current_price_id=current_price_id,
        growthPercentage=percentage,
        increasePayTerms=terms,
        how_many_times=how_many_times
    )
    match section:
        case 'service':
            service_term.forService_id = pk
            service_term.increaseDay = datetime.datetime.today() + get_increase_date(terms, how_many_times)
            service_term.new_price = ((current_price * percentage) / 100) + current_price
        case 'commodity':
            service_term.forCommodity_id = pk
            service_term.increaseDay = datetime.datetime.today() + get_increase_date(terms, how_many_times)
            service_term.new_price = ((current_price * percentage) / 100) + current_price
        case 'consultant':
            service_term.forConsultant_id = pk
            service_term.increaseDay = datetime.datetime.today() + get_increase_date(terms, how_many_times)
            print("????????????????????????")
            service_term.new_price = ((current_price * percentage) / 100) + current_price
    service_term.save()


@app.task
def auto_create_increase_terms():
    increase_pay_terms = ServiceCommodityConsultantPayTermsIncrease.objects.select_related(
        'organization', 'forCommodity', 'forService', 'forConsultant', 'current_price'
    ).filter(increaseDay=datetime.datetime.today(), is_active=True, changed_to_new_price=False)
    if increase_pay_terms:
        with transaction.atomic():
            for pay_term in increase_pay_terms:
                if pay_term.forService is not None:
                    if pay_term.forService.must_increase:
                        service_current_price = create_new_price(
                            pay_term.organization.id,
                            pay_term.forService.id,
                            pay_term.new_price,
                            'service'
                        )
                        create_first_increase_terms(
                            organization_id=pay_term.organization.id,
                            pk=pay_term.forService.id,
                            current_price_id=service_current_price.id,
                            current_price=service_current_price.price,
                            percentage=pay_term.growthPercentage,
                            terms=pay_term.increasePayTerms,
                            how_many_times=pay_term.forService.how_many_times,
                            section='service'
                        )
                        send_email_to_service_creator(pay_term.forService.creator.email)

                if pay_term.forCommodity is not None:
                    if pay_term.forCommodity.must_increase:
                        commodity_current_price = create_new_price(
                            pay_term.organization.id,
                            pay_term.forCommodity.id,
                            pay_term.new_price,
                            'commodity'
                        )
                        create_first_increase_terms(
                            organization_id=pay_term.organization.id,
                            pk=pay_term.forCommodity.id,
                            current_price_id=commodity_current_price.id,
                            current_price=commodity_current_price.price,
                            percentage=pay_term.growthPercentage,
                            terms=pay_term.increasePayTerms,
                            how_many_times=pay_term.forCommodity.how_many_times,
                            section='commodity'
                        )
                        send_email_to_service_creator(pay_term.forCommodity.creator.email)

                if pay_term.forConsultant is not None:
                    if pay_term.forConsultant.must_increase:
                        consultant_current_price = create_new_price(
                            pay_term.organization.id,
                            pay_term.forConsultant.id,
                            pay_term.new_price,
                            'consultant'
                        )
                        create_first_increase_terms(
                            organization_id=pay_term.organization.id,
                            pk=pay_term.forConsultant.id,
                            current_price_id=consultant_current_price.id,
                            current_price=consultant_current_price.price,
                            percentage=pay_term.growthPercentage,
                            terms=pay_term.increasePayTerms,
                            how_many_times=pay_term.forConsultant.how_many_times,
                            section='consultant'
                        )
                        send_email_to_service_creator(pay_term.forConsultant.creator.email)
                pay_term.changed_to_new_price = True
                pay_term.is_active = False
                pay_term.save()


@app.task
def check_organization_service_commodity_consultant_status():
    organizations = Organization.objects.values_list('id')
    with transaction.atomic():
        contract_services = ContractService.objects.select_related('contract', 'service', 'creator')
        contract_commodities = ContractCommodity.objects.select_related('contract', 'commodity', 'creator')
        contract_consultants = ContractConsultant.objects.select_related('contract', 'consultant', 'creator')

        services = Service.objects.select_related('organization', 'creator')
        commodities = Commodity.objects.select_related('organization', 'creator')
        consultants = Consultant.objects.select_related('organization', 'creator')

        for organization in organizations:
            check_service_status(organization[0], contract_services, services)
            check_commodity_status(organization[0], contract_commodities, commodities)
            check_consultant_status(organization[0], contract_consultants, consultants)


def check_service_status(organization, contract_services, services):
    with transaction.atomic():
        if services.filter(organization_id=organization):
            for service in services:
                if not contract_services.filter(service_id=service.id):
                    service.status = 'inactive'
                if contract_services.filter(contract__status__in=['EXPIRED', 'DRAFT', 'NEW'], service_id=service.id).exists():
                    service.status = 'expired'
                if contract_services.filter(contract__status='ACTIVE', service_id=service.id).exists():
                    service.status = 'active'
                service.save()


def check_commodity_status(organization, contract_commodities, commodities):
    with transaction.atomic():
        if commodities.filter(organization_id=organization):
            for commodity in commodities:
                if not contract_commodities.filter(commodity_id=commodity.id):
                    commodity.status = 'inactive'
                if contract_commodities.filter(contract__status__in=['EXPIRED', 'DRAFT', 'NEW'],
                                            commodity_id=commodity.id).exists():
                    commodity.status = 'expired'
                if contract_commodities.filter(contract__status='ACTIVE', commodity_id=commodity.id).exists():
                    commodity.status = 'active'
                commodity.save()


def check_consultant_status(organization, contract_consultants, consultants):
    with transaction.atomic():
        if consultants.filter(organization_id=organization):
            for consultant in consultants:
                if not contract_consultants.filter(consultant_id=consultant.id):
                    consultant.status = 'inactive'
                if contract_consultants.filter(contract__status__in=['EXPIRED', 'DRAFT', 'NEW'],
                                            consultant_id=consultant.id).exists():
                    consultant.status = 'expired'
                if contract_consultants.filter(contract__status='ACTIVE', consultant_id=consultant.id).exists():
                    consultant.status = 'active'
                consultant.save()
