from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('votingsystembase.urls')),
    path('superadmin/', include('django.contrib.auth.urls')),
    path('superadmin/', include('superadmin.urls')),
    path('VotingAdmin/', include('django.contrib.auth.urls')),
    path('VotingAdmin/', include('VotingAdmin.urls')),
    path('Voters/', include('Voters.urls')),
    path('Voters/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
