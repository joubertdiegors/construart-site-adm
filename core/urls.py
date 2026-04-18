from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from . import views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('login/', views.login_view, name='login'),
    path('setup-inicial-4x9z/', views.setup_view, name='setup'),
]

urlpatterns += i18n_patterns(
    path('', views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('subcontractors/', include('subcontractors.urls')),
    path('planning/', include('planning.urls')),
    path('clients/', include('clients.urls')),
    path('workforce/', include('workforce.urls')),
    path('timesheets/', include('timesheets.urls')),
)
