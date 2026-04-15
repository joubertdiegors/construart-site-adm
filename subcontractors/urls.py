# subcontractors/urls.py

from django.urls import path
from . import views

app_name = 'subcontractors'

urlpatterns = [
    path('', views.subcontractor_list, name='list'),
    path('create/', views.subcontractor_create, name='create'),
    path('<int:pk>/edit/', views.subcontractor_update, name='update'),
]