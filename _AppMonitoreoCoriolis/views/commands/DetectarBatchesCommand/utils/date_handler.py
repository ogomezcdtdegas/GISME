"""
Utilidades para manejo de fechas y zonas horarias.
"""
import pytz
from datetime import datetime
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ


def parse_and_validate_dates(fecha_inicio_str, fecha_fin_str):
    """
    Parsea y valida fechas del frontend, convirtiéndolas de Colombia a UTC.
    
    Args:
        fecha_inicio_str (str): Fecha inicio en formato YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS
        fecha_fin_str (str): Fecha fin en formato YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS
        
    Returns:
        dict: {
            'fecha_inicio_utc': datetime,
            'fecha_fin_utc': datetime,
            'fecha_inicio_colombia': datetime,
            'fecha_fin_colombia': datetime
        } o {'error': str}
    """
    try:
        # Intentar formato con fecha y hora: "2025-10-16T00:00:00"
        fecha_inicio_naive = datetime.strptime(fecha_inicio_str, '%Y-%m-%dT%H:%M:%S')
        fecha_fin_naive = datetime.strptime(fecha_fin_str, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        try:
            # Fallback a formato solo fecha: "2025-10-16"
            fecha_inicio_naive = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            fecha_fin_naive = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            # Establecer horas para cubrir todo el rango del día
            fecha_inicio_naive = fecha_inicio_naive.replace(hour=0, minute=0, second=0, microsecond=0)
            fecha_fin_naive = fecha_fin_naive.replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            return {'error': 'Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS'}
    
    # Asumir que las fechas del frontend están en hora de Colombia y convertir a UTC
    fecha_inicio_colombia = COLOMBIA_TZ.localize(fecha_inicio_naive)
    fecha_fin_colombia = COLOMBIA_TZ.localize(fecha_fin_naive)
    
    # Convertir a UTC para consultas de base de datos
    fecha_inicio_utc = fecha_inicio_colombia.astimezone(pytz.UTC)
    fecha_fin_utc = fecha_fin_colombia.astimezone(pytz.UTC)
    
    return {
        'fecha_inicio_utc': fecha_inicio_utc,
        'fecha_fin_utc': fecha_fin_utc,
        'fecha_inicio_colombia': fecha_inicio_colombia,
        'fecha_fin_colombia': fecha_fin_colombia
    }
