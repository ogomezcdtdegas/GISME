"""
Vistas refactorizadas para Monitoreo Coriolis
Estructura modular CQS (Command Query Separation)

Este archivo mantiene compatibilidad con URLs existentes
importando desde la nueva estructura modular.
"""

# Importar todas las vistas desde la estructura modular
from .views import *

# Re-exportar utilidades para compatibilidad
from .views.utils import (
    get_coeficientes_correccion,
    convertir_presion_con_span,
    COLOMBIA_TZ
)