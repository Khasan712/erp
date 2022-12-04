from django.contrib import admin
from .models import (
    Supplier,
    SupplierQuestionary,
    SupplierQuestionaryAnswer,
    SupplierQuestionaryResult
)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'supplier', 'parent')


@admin.register(SupplierQuestionary)
class SupplierQuestionaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'title', 'general_status', 'weight', 'parent', 'created_at')


@admin.register(SupplierQuestionaryAnswer)
class SupplierQuestionaryAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'checker', 'question', 'yes_no', 'is_true', 'weight', 'answered_at', 'checked_at')


@admin.register(SupplierQuestionaryResult)
class SupplierQuestionaryResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'checker', 'questionary', 'total_weight', 'questionary_status', 'created_at')


