"""
Utilidades para decimación inteligente de datos de series temporales.
Reduce la cantidad de puntos sin perder la forma de la curva.
"""
import logging

logger = logging.getLogger(__name__)


def decimar_datos_inteligente(datos, max_puntos=2000):
    """
    Reduce la cantidad de puntos de datos manteniendo la forma de la curva.
    
    Estrategia:
    - Si hay menos de max_puntos, devuelve todos los datos
    - Si hay más, toma 1 de cada N puntos de forma uniforme
    - Siempre incluye el primer y último punto
    
    Args:
        datos: QuerySet o lista de objetos de datos
        max_puntos: Cantidad máxima de puntos a devolver (default: 2000)
        
    Returns:
        Lista reducida de datos
    """
    datos_list = list(datos)
    total_puntos = len(datos_list)
    
    if total_puntos <= max_puntos:
        logger.info(f"📊 Datos: {total_puntos} puntos (no requiere decimación)")
        return datos_list
    
    # Calcular factor de decimación
    factor = total_puntos / max_puntos
    logger.info(f"📊 Decimación: {total_puntos} → ~{max_puntos} puntos (factor: {factor:.2f}x)")
    
    datos_decimados = []
    
    # Siempre incluir el primer punto
    datos_decimados.append(datos_list[0])
    
    # Tomar puntos uniformemente distribuidos
    indice_float = factor
    while indice_float < total_puntos - 1:
        indice = int(indice_float)
        if indice < total_puntos:
            datos_decimados.append(datos_list[indice])
        indice_float += factor
    
    # Siempre incluir el último punto
    if datos_list[-1] not in datos_decimados:
        datos_decimados.append(datos_list[-1])
    
    logger.info(f"✅ Decimación completada: {len(datos_decimados)} puntos finales")
    return datos_decimados


def calcular_estadisticas_decimacion(total_original, total_decimado):
    """
    Calcula estadísticas sobre la decimación aplicada.
    
    Args:
        total_original: Cantidad original de puntos
        total_decimado: Cantidad de puntos después de decimación
        
    Returns:
        Diccionario con estadísticas
    """
    if total_original == 0:
        return {
            'total_original': 0,
            'total_decimado': 0,
            'decimacion_aplicada': False,
            'factor_reduccion': 1.0,
            'porcentaje_reduccion': 0.0
        }
    
    decimacion_aplicada = total_original > total_decimado
    factor_reduccion = total_original / total_decimado if total_decimado > 0 else 1.0
    porcentaje_reduccion = ((total_original - total_decimado) / total_original * 100) if decimacion_aplicada else 0.0
    
    return {
        'total_original': total_original,
        'total_decimado': total_decimado,
        'decimacion_aplicada': decimacion_aplicada,
        'factor_reduccion': round(factor_reduccion, 2),
        'porcentaje_reduccion': round(porcentaje_reduccion, 1)
    }
