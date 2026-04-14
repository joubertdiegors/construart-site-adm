from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # 👈 sempre fora
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('projects/', include('projects.urls')),
)
