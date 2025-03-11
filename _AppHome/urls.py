from django.urls import path
from .views import allEquiposPag, crearEquipo

urlpatterns = [
    path('allEquiposPag/', allEquiposPag.as_view(), name='allEquiposPag'),  # 📌 Listar equipos con paginación
    path('crear-equipo/', crearEquipo.as_view(), name='crearEquipo'),  # 📌 Crear equipo
]
