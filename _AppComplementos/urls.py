from django.urls import path
from .views.criticidad import allCriticidadPag, crearCriticidad, editarCriticidad

urlpatterns = [
    path('', allCriticidadPag.as_view(), name='allCriticidadesPag'),  # 📌 Listar equipos con paginación
    path('crear-criticidad/', crearCriticidad.as_view(), name='crearCriticidad'),  # 📌 Crear equipo
    path('editar-criticidad/<uuid:obj_id>/', editarCriticidad.as_view(), name='editarCriticidad'), # 📌 Editar equipo
]
