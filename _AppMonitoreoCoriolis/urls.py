from django.urls import path
from . import views
from .views_node_red import NodeRedReceiverView
from .views.queries.pdf_views import DescargarTicketBatchPDFView

urlpatterns = [
    # Vistas principales SPA (CBVs)
    path('', views.MonitoreoCoriolisBaseView.as_view(), name='monitoreo_coriolis'),
    path('sistema/<uuid:sistema_id>/', views.MonitoreoCoriolisSistemaView.as_view(), name='monitoreo_coriolis_sistema'),
    
    # APIs para datos históricos (CBVs)
    path('api/datos-flujo/<uuid:sistema_id>/', views.DatosHistoricosFlujoView.as_view(), name='datos_flujo'),
    path('api/datos-presion/<uuid:sistema_id>/', views.DatosHistoricosPresionView.as_view(), name='datos_presion'),
    path('api/datos-temperatura/<uuid:sistema_id>/', views.DatosHistoricosTemperaturaView.as_view(), name='datos_temperatura'),
    path('api/datos-otras-variables/<uuid:sistema_id>/', views.DatosHistoricosOtrasVariablesView.as_view(), name='datos_otras_variables'),
    path('api/datos-tiempo-real/<uuid:sistema_id>/', views.DatosTiempoRealView.as_view(), name='datos_tiempo_real'),
    path('api/datos-tendencias/<uuid:sistema_id>/', views.DatosTendenciasView.as_view(), name='datos_tendencias'),
    
    # API para detección de batches
    path('api/detectar-batches/<uuid:sistema_id>/', views.DetectarBatchesView.as_view(), name='detectar_batches'),
    path('api/listar-batches/<uuid:sistema_id>/', views.ListarBatchesView.as_view(), name='listar_batches'),
    path('api/listar-tickets/<uuid:sistema_id>/', views.ListarTicketsQueryView.as_view(), name='listar_tickets'),
    path('api/listar-todos-tickets/<uuid:sistema_id>/', views.ListarTodosTicketsView.as_view(), name='listar_todos_tickets'),
    path('api/asignar-ticket-batch/<uuid:batch_id>/', views.AsignarTicketBatchView.as_view(), name='asignar_ticket_batch'),
    path('api/detalle-batch/<uuid:batch_id>/', views.DetalleBatchView.as_view(), name='detalle_batch'),
    path('api/configuracion/actualizar/<uuid:sistema_id>/', views.ActualizarConfiguracionView.as_view(), name='actualizar_configuracion'),
    
    # PDF Downloads
    path('pdf/ticket-batch/<uuid:batch_id>/', DescargarTicketBatchPDFView.as_view(), name='descargar_ticket_batch_pdf'),
]

urlpatterns += [
    # Endpoint para Node-RED
    path('api/node-red/', NodeRedReceiverView.as_view(), name='node_red_receiver'),
]
