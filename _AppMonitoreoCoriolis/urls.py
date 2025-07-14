from django.urls import path
from . import views

urlpatterns = [
    path('', views.monitoreo_coriolis_index, name='monitoreo_coriolis'),
    path('<uuid:sistema_id>/', views.monitoreo_coriolis_sistema, name='monitoreo_coriolis_sistema'),
]
