from django.urls import path
from . import views

urlpatterns = [
    # Vista base SPA - Una sola ruta que maneja todo
    path('', views.MonitoreoCoriolisBaseView.as_view(), name='monitoreo_coriolis'),
    path('<uuid:sistema_id>/', views.MonitoreoCoriolisBaseView.as_view(), name='monitoreo_coriolis_sistema')
]
