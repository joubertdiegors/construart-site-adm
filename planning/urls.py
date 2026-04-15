from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    path('', views.planning_list, name='list'),
    path('project/<int:project_pk>/create/', views.planning_create, name='create'),
    path('<int:pk>/', views.planning_detail, name='detail'),
    path('<int:pk>/delete/', views.planning_delete, name='delete'),

    # API JSON — workers
    path('<int:planning_pk>/workers/add/', views.planning_add_worker, name='add_worker'),
    path('workers/<int:pw_pk>/update/', views.planning_update_worker, name='update_worker'),
    path('workers/<int:pw_pk>/remove/', views.planning_remove_worker, name='remove_worker'),

    # API JSON — subcontractors
    path('<int:planning_pk>/subcontractors/add/', views.planning_add_subcontractor, name='add_subcontractor'),
    path('subcontractors/<int:ps_pk>/remove/', views.planning_remove_subcontractor, name='remove_subcontractor'),
]