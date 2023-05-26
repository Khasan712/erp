from django.contrib import admin

from .models import (
    SourcingRequest,
    SourcingRequestEvent,
    SourcingRequestEventSuppliers,
    SupplierAnswer,
    SupplierResult,
    # EventQuestionary
    CategoryRequest,
    DocumentSourcing,
    SourcingRequestService, SourcingRequestCommodity, SourcingRequestConsultant,
    SourcingRequestAssigned, SourcingComments, SourcingCommentFile
)


admin.site.register(SourcingRequest)


@admin.register(SourcingRequestEvent)
class SourcingRequestEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'sourcing_request', 'creator', 'sourcing_event', 'title', 'general_status', 'parent', 'weight')
    list_filter = ('sourcing_event', 'general_status')


# @admin.register(EventQuestionary)
# class EventQuestionaryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'sourcing_request', 'creator', 'sourcing_event', 'title', 'general_status', 'parent', 'weight')


@admin.register(SourcingRequestEventSuppliers)
class SourcingRequestEventSuppliersAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'sourcingRequestEvent', 'supplier_timeline', 'get_total_weight')


@admin.register(CategoryRequest)
class CategoryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization')


@admin.register(SupplierAnswer)
class SupplierAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'question', 'yes_no', 'checker', 'weight', 'answered_at', 'checked_at')


@admin.register(SupplierResult)
class SupplierResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'questionary', 'supplier', 'questionary_status', 'total_weight')


@admin.register(DocumentSourcing)
class DocumentSourcingAdmin(admin.ModelAdmin):
    list_display = ('id', 'sourcingRequest', 'sourcingEvent',)


admin.site.register(SourcingRequestService)
admin.site.register(SourcingRequestCommodity)
admin.site.register(SourcingRequestConsultant)
admin.site.register(SourcingRequestAssigned)
admin.site.register(SourcingComments)
admin.site.register(SourcingCommentFile)
