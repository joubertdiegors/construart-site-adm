from django.contrib import admin
from .models import Subcontractor


@admin.register(Subcontractor)
class SubcontractorAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'vat_number',
        'phone',
        'status',
        'created_at'
    )

    list_filter = ('status',)

    search_fields = (
        'name',
        'vat_number',
        'contact_name',
        'email'
    )

    ordering = ('name',)