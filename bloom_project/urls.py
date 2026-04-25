"""
Bloom — mothership URL configuration
All app URLs are namespaced and included here.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Empty path required by spec
    path('', include('core.urls')),

    # App URLs — referenced by nickname (app_name)
    path('accounts/', include('accounts.urls')),
    path('catalogue/', include('catalogue.urls')),
    path('shop/', include('shop.urls')),
    path('donations/', include('donations.urls')),
    path('panel/', include('admin_panel.urls')),

    # Django built-in admin (kept as fallback)
    path('django-admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'bloom_project.views.handler404'
handler403 = 'bloom_project.views.handler403'
