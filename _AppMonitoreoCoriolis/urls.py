from django.urls import path
from . import views
from .views_node_red import NodeRedReceiverView

urlpatterns = [
    # Vistas principales SPA (CBVs)
    path('', views.MonitoreoCoriolisBaseView.as_view(), name='monitoreo_coriolis'),
    path('sistema/<uuid:sistema_id>/', views.MonitoreoCoriolisSistemaView.as_view(), name='monitoreo_coriolis_sistema'),
    
    # APIs para datos históricos (CBVs)
    path('api/datos-flujo/<uuid:sistema_id>/', views.DatosHistoricosFlujoView.as_view(), name='datos_flujo'),
    path('api/datos-tiempo-real/<uuid:sistema_id>/', views.DatosTiempoRealView.as_view(), name='datos_tiempo_real'),
]

urlpatterns += [
    # Endpoint para Node-RED
    path('api/node-red/', NodeRedReceiverView.as_view(), name='node_red_receiver'),
]
