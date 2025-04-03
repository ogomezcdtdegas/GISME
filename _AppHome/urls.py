from django.urls import path

from .views.views_Equipo.Commands import CreateEquipoCommand, UpdateEquipoCommand
from .views.views_Equipo.Queries import GetAllEquipoPagQuery

urlpatterns = [
    path('', GetAllEquipoPagQuery.allEquiposPag.as_view(), name='allEquiposPag'),  # 📌 Listar equipos con paginación
    path('crear-equipo/', CreateEquipoCommand.crearEquipo.as_view(), name='crearEquipo'),  # 📌 Crear equipo
    path('editar-equipo/<uuid:obj_id>/', UpdateEquipoCommand.editarEquipo.as_view(), name='editarEquipo'), # 📌 Editar equipo
]
