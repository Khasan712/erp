from django.contrib import admin
from .models import (
    Category,
    Contract,
    ContractNotificationDay,
    Currency,
    Departement, ContractService, ContractConsultant, ContractCommodity,
    ContractTask,
    ConnectContractWithTask,
    DocumentContact,
    ContractExpirationDayAndStatus
)
from .history_contract_models import HistoryContract

# Register your models here.


admin.site.register(Category)
admin.site.register(HistoryContract)
admin.site.register(ContractExpirationDayAndStatus)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contract_number', 'status', 'currency', 'contract_amount', 'create_by',
                    'category_manager', 'organization')


@admin.register(ContractNotificationDay)
class ContractNotificationDayAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'send_email_day', 'is_send')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'created_at')


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'creator', 'created_at')


@admin.register(ContractTask)
class ContractTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'name', 'created_at')


@admin.register(ConnectContractWithTask)
class ConnectContractWithTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract_id', 'task', 'executor', 'is_done', 'created_at')


@admin.register(DocumentContact)
class DocumentContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'contract', 'is_signing')


admin.site.register(ContractService)
admin.site.register(ContractConsultant)
admin.site.register(ContractCommodity)
