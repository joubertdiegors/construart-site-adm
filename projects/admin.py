from django.contrib import admin
from .models import Project, WorkRegistrationType


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    # 📋 LISTAGEM
    list_display = (
        'name',
        'client',
        'get_managers',
        'start_date',
        'end_date',
        'is_active',
        'has_work_registration',
    )

    # 🔍 FILTROS
    list_filter = (
        'is_active',
        'has_work_registration',
        'client',
        'managers',
    )

    # 🔎 BUSCA
    search_fields = (
        'name',
        'client__name',
        'address',
    )

    # 🧩 MANY TO MANY BONITO
    filter_horizontal = (
        'managers',
        'contacts',
    )

    # 📑 ORGANIZAÇÃO DO FORM
    fieldsets = (
        ("General", {
            'fields': (
                'name',
                'client',
                'contacts',
                'address',
            )
        }),
        ("Team", {
            'fields': (
                'managers',
            )
        }),
        ("Dates", {
            'fields': (
                'start_date',
                'end_date',
            )
        }),
        ("Work Registration", {
            'fields': (
                'has_work_registration',
                'work_registration_type',
                'work_registration_number',
            )
        }),
        ("Notes", {
            'fields': (
                'notes',
            )
        }),
        ("Status", {
            'fields': (
                'is_active',
            )
        }),
    )

    # 👤 EXIBIR MANY TO MANY NA LISTA
    def get_managers(self, obj):
        return ", ".join([str(user) for user in obj.managers.all()])

    get_managers.short_description = "Managers"


@admin.register(WorkRegistrationType)
class WorkRegistrationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)