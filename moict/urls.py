from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard:index'), name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('employees/', include('employees.urls', namespace='employees')),
    path('schemes/', include('schemes.urls', namespace='schemes')),
    path('announcements/', include('announcements.urls', namespace='announcements')),
    path('inquiries/', include('inquiries.urls', namespace='inquiries')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('core/', include('core.urls', namespace='core')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.error_404'
handler403 = 'core.views.error_403'
