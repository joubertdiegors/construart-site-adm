from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

from audit.admin_mixins import AuditHistoryMixin


@admin.register(User)
class CustomUserAdmin(AuditHistoryMixin, UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Informações adicionais", {
            "fields": ("phone", "is_manager"),
        }),
        ("Auditoria", {
            "fields": ("audit_history",),
        }),
    )

    readonly_fields = UserAdmin.readonly_fields + ('audit_history',)