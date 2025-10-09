"""
Utilidades compartidas para las vistas de monitoreo de Coriolis
"""
import pytz
import logging
from _AppComplementos.models import ConfiguracionCoeficientes

# Configurar logging
logger = logging.getLogger(__name__)

# Configurar zona horaria de Colombia
COLOMBIA_TZ = pytz.timezone('America/Bogota')

def get_coeficientes_correccion(sistema):
    """
    Obtiene los coeficientes de corrección para un sistema.
    Retorna valores por defecto (m=1, b=0) si no existen configuraciones.
    """
    try:
        coef = ConfiguracionCoeficientes.objects.get(systemId=sistema)
        return coef.mt, coef.bt, coef.mp, coef.bp, coef.span_presion, coef.zero_presion
    except ConfiguracionCoeficientes.DoesNotExist:
        # Valores por defecto: m=1, b=0 (no corrige), span=1, zero=0
        return 1.0, 0.0, 1.0, 0.0, 1.0, 0.0

def convertir_presion_con_span(valor_crudo, span_presion):
    """
    Convierte el valor crudo de presión usando el span del sistema.
    """
    return valor_crudo / span_presion