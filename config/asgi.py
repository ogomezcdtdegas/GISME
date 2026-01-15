"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Inicializar Django ASGI application primero
django_asgi_app = get_asgi_application()

# Importar después de inicializar Django
from _AppMonitoreoCoriolis.routing import websocket_urlpatterns
from _AppAuth.middleware_msal import MSALAuthMiddleware

# ====================================================
# ASGI Application con Redis y autenticación
# ====================================================
# Configuración optimizada para WebSockets con:
#   - AuthMiddlewareStack: Maneja sesiones Django y autenticación básica
#   - URLRouter: Enruta conexiones WebSocket
#   - Redis (Channel Layers): Distribuye mensajes entre workers
#
# NOTA: MSALAuthMiddleware removido temporalmente porque es MiddlewareMixin (HTTP)
# y no es compatible con ASGI WebSockets. La autenticación se maneja via sesión Django.

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
