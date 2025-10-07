from django.urls import path
from . import views
from .views_node_red import NodeRedReceiverView

urlpatterns = [
    # Vistas principales SPA (CBVs)
    path('', views.MonitoreoCoriolisBaseView.as_view(), name='monitoreo_coriolis'),
    path('sistema/<uuid:sistema_id>/', views.MonitoreoCoriolisSistemaView.as_view(), name='monitoreo_coriolis_sistema'),
    
    # APIs para datos históricos (CBVs)
    path('api/datos-flujo/<uuid:sistema_id>/', views.DatosHistoricosFlujoView.as_view(), name='datos_flujo'),
    path('api/datos-presion/<uuid:sistema_id>/', views.DatosHistoricosPresionView.as_view(), name='datos_presion'),
    path('api/datos-temperatura/<uuid:sistema_id>/', views.DatosHistoricosTemperaturaView.as_view(), name='datos_temperatura'),
    path('api/datos-tiempo-real/<uuid:sistema_id>/', views.DatosTiempoRealView.as_view(), name='datos_tiempo_real'),
    path('api/datos-tendencias/<uuid:sistema_id>/', views.DatosTendenciasView.as_view(), name='datos_tendencias'),
    
    # API para detección de batches
    path('api/detectar-batches/<uuid:sistema_id>/', views.DetectarBatchesView.as_view(), name='detectar_batches'),
]

urlpatterns += [
    # Endpoint para Node-RED
    path('api/node-red/', NodeRedReceiverView.as_view(), name='node_red_receiver'),
]
