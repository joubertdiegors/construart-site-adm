from django.contrib import admin
from .models import Planning, PlanningWorker, PlanningSubcontractor


class PlanningWorkerInline(admin.TabularInline):
    model = PlanningWorker
    fk_name = 'planning'
    extra = 1


class PlanningSubcontractorInline(admin.TabularInline):
    model = PlanningSubcontractor
    fk_name = 'planning'
    extra = 1


@admin.register(Planning)
class PlanningAdmin(admin.ModelAdmin):
    list_display = ('project', 'date')
    list_filter = ('date', 'project')
    search_fields = ('project__name',)

    inlines = [
        PlanningSubcontractorInline,
        PlanningWorkerInline,
    ]