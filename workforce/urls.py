from django.urls import path
from . import views

app_name = 'workforce'

urlpatterns = [
    path('', views.collaborator_list, name='list'),
    path('create/', views.collaborator_create, name='create'),
    path('<int:pk>/edit/', views.collaborator_update, name='update'),
]