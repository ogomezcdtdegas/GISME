"""
Generación de hash único para identificación de batches.
"""
import hashlib


def generate_batch_hash(fecha_inicio, fecha_fin, sistema_id, vol_minimo, time_finished_batch):
    """
    Genera un hash único basado en las fechas, sistema ID, vol_minimo y time_finished_batch.
    Esto previene duplicados cuando se ejecuta la detección múltiples veces.
    
    Args:
        fecha_inicio (datetime): Fecha de inicio del batch
        fecha_fin (datetime): Fecha de fin del batch
        sistema_id (str): UUID del sistema
        vol_minimo (float): Volumen mínimo usado en la detección
        time_finished_batch (float): Tiempo de espera usado
        
    Returns:
        str: Hash SHA-256 hexadecimal
    """
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
    
    datos_hash = f"{sistema_id}_{fecha_inicio_str}_{fecha_fin_str}_{vol_minimo}_{time_finished_batch}"
    
    hash_obj = hashlib.sha256(datos_hash.encode('utf-8'))
    return hash_obj.hexdigest()
