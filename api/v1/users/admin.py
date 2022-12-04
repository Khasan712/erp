from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    User
)


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'organization', 'phone')
