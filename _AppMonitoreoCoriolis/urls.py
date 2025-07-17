from django.urls import path
from . import views
from .views_node_red import NodeRedReceiverView

urlpatterns = [
    # Vista base SPA - Una sola ruta que maneja todo
    path('', views.MonitoreoCoriolisBaseView.as_view(), name='monitoreo_coriolis'),
    path('<uuid:sistema_id>/', views.MonitoreoCoriolisBaseView.as_view(), name='monitoreo_coriolis_sistema')
]

urlpatterns += [
    # Endpoint para Node-RED
    path('api/node-red/', NodeRedReceiverView.as_view(), name='node_red_receiver'),
]
