from django.urls import path
from .views.criticidad import allCriticidadPag, crearCriticidad, editarCriticidad
from .views.tipo_criticidad import allTipCriticidadPag,crearTipCriticidad,editarTipCriticidad, CriticidadListAllView

urlpatterns = [
    path('', allCriticidadPag.as_view(), name='allCriticidadesPag'),  # 📌 Listar equipos con paginación
    path('crear-criticidad/', crearCriticidad.as_view(), name='crearCriticidad'),  # 📌 Crear equipo
    path('editar-criticidad/<uuid:obj_id>/', editarCriticidad.as_view(), name='editarCriticidad'), # 📌 Editar equipo


    path('tipCriticidades/', allTipCriticidadPag.as_view(), name='allTipCriticidadesPag'),  # 📌 Listar equipos con paginación
    path('crear-tipCriticidad/', crearTipCriticidad.as_view(), name='crearTipCriticidad'),  # 📌 Crear equipo
    path('editar-tipCriticidad/<uuid:obj_id>/', editarTipCriticidad.as_view(), name='editarTipCriticidad'), # 📌 Editar equipo

    path('listar-todo-criticidad/', CriticidadListAllView.as_view(), name='listarTodoCriticidad'),  # 🔹 Nueva ruta
]
