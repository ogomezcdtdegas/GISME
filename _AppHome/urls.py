from django.urls import path
from . import views

urlpatterns = [
    path('allEquiposPag/', views.allEquiposPag, name='allEquiposPag'),  # 📌 Ruta para la página de inicio
    path('crear-equipo/', views.crearEquipo, name='crearEquipo'),
]