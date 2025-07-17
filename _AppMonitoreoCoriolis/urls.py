from django.urls import path
from . import views
from .views_node_red import node_red_receiver

urlpatterns = [
    # Vista base SPA - Una sola ruta que maneja todo
    path('', views.MonitoreoCoriolisBaseView.as_view(), name='monitoreo_coriolis'),
    path('<uuid:sistema_id>/', views.MonitoreoCoriolisBaseView.as_view(), name='monitoreo_coriolis_sistema')
]

urlpatterns += [
    # Endpoint para Node-RED
    path('api/node-red/', node_red_receiver, name='node_red_receiver'),
]
