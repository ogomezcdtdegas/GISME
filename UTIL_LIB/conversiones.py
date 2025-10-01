"""
Utilidades de conversión para el sistema de monitoreo Coriolis
Convierte unidades de medida según los requerimientos del frontend
"""

def celsius_a_fahrenheit(celsius):
    """
    Convierte temperatura de Celsius a Fahrenheit
    Args:
        celsius (float): Temperatura en grados Celsius
    Returns:
        float: Temperatura en grados Fahrenheit
    """
    if celsius is None:
        return 0
    try:
        return float(celsius) * 9.0 / 5.0 + 32.0
    except (ValueError, TypeError):
        return 0

def lb_s_a_kg_min(lb_s):
    """
    Convierte flujo másico de libras por segundo a kilogramos por minuto
    Args:
        lb_s (float): Flujo másico en lb/s
    Returns:
        float: Flujo másico en kg/min
    """
    if lb_s is None:
        return 0
    try:
        return float(lb_s) * 0.453592 * 60
    except (ValueError, TypeError):
        return 0

def cm3_s_a_m3_min(cm3_s):
    """
    Convierte flujo volumétrico de cm³/s a m³/min
    Args:
        cm3_s (float): Flujo volumétrico en cm³/s
    Returns:
        float: Flujo volumétrico en m³/min
    """
    if cm3_s is None:
        return 0
    try:
        return float(cm3_s) / 1_000_000.0 * 60
    except (ValueError, TypeError):
        return 0

def cm3_a_m3(cm3):
    """
    Convierte volumen de cm³ a m³
    Args:
        cm3 (float): Volumen en cm³
    Returns:
        float: Volumen en m³
    """
    if cm3 is None:
        return 0
    try:
        return float(cm3) / 1_000_000.0
    except (ValueError, TypeError):
        return 0

def lb_a_kg(lb):
    """
    Convierte masa de libras a kilogramos
    Args:
        lb (float): Masa en libras
    Returns:
        float: Masa en kilogramos
    """
    if lb is None:
        return 0
    try:
        return float(lb) * 0.453592
    except (ValueError, TypeError):
        return 0

def formatear_numero(valor, decimales=2):
    """
    Formatea un número con la cantidad especificada de decimales
    Args:
        valor (float): Valor a formatear
        decimales (int): Número de decimales
    Returns:
        str: Número formateado como string
    """
    if valor is None:
        return "---"
    return f"{valor:.{decimales}f}"