from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('_AppHome.urls')),
    path('monitoreo/', include('_AppMonitoreoCoriolis.urls')),
    path('complementos/', include('_AppComplementos.urls')),
    path('auth/', include('_AppAuth.urls')),
    path('admin_panel/', include('_AppAdmin.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if not settings.USE_EASYAUTH:
    from _AppAuth.views_aad_local import aad_login, aad_callback, aad_logout
    urlpatterns += [
        path("aad/login", aad_login, name="aad_login"),
        path("aad/callback", aad_callback, name="aad_callback"),
        path("aad/logout", aad_logout, name="aad_logout"),
    ]

