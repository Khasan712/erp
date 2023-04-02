from django.contrib import admin

from api.v1.reports.models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_model', 'done_by', 'created_at')
