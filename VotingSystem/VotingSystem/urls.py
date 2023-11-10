from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('votingsystembase.urls')),
    path('superadmin/', include('django.contrib.auth.urls')),
    path('superadmin/', include('superadmin.urls')),
    path('VotingAdmin/', include('django.contrib.auth.urls')),
    path('VotingAdmin/', include('VotingAdmin.urls')),
]
