from django.contrib import admin

# Register your models here.
from .models import (
    Organization,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')