from django.urls import re_path
from . import consumers

# Patrones de URL para WebSockets
websocket_urlpatterns = [
    re_path(r'ws/tendencias/(?P<sistema_id>[0-9a-f-]+)/$', consumers.TendenciasConsumer.as_asgi()),
]
