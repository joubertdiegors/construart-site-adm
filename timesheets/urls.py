from django.urls import path
from . import views

app_name = 'timesheets'

urlpatterns = [
    path('',                                    views.timesheet_list,             name='list'),
    path('create/',                             views.timesheet_create,           name='create'),
    path('<int:pk>/edit/',                      views.timesheet_update,           name='update'),
    path('<int:pk>/delete/',                    views.timesheet_delete,           name='delete'),
    path('project/<int:project_pk>/summary/',   views.timesheet_project_summary,  name='project_summary'),
    path('planning/<int:planning_pk>/bulk/',    views.timesheet_bulk_from_planning, name='bulk_from_planning'),
]
