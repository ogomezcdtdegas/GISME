"""
Servicio para cálculo de masa total bruta.
"""
import logging
from UTIL_LIB.conversiones import lb_s_a_kg_min, lb_a_kg
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ

logger = logging.getLogger(__name__)


class MassCalculatorService:
    """
    Calcula la masa total bruta del rango SIN considerar perfil de detección.
    Solo cuenta cuando hay flujo (mass_rate > 0) y detecta resets automáticamente.
    """
    
    def calculate_total_mass(self, datos, fecha_inicio, fecha_fin):
        """
        Calcula masa total acumulada en el rango.
        
        Args:
            datos: QuerySet de NodeRedData ordenado por created_at_iot
            fecha_inicio (datetime): Inicio del rango en UTC
            fecha_fin (datetime): Fin del rango en UTC
            
        Returns:
            float: Masa total acumulada en kg
        """
        masa_total_acumulada = 0.0
        masa_anterior = None
        registros_procesados = 0
        resets_detectados = 0
        
        for dato in datos:
            # Filtrar solo datos dentro del rango exacto (sin margen)
            if not (fecha_inicio <= dato.created_at_iot <= fecha_fin):
                continue
                
            mass_rate_raw = dato.mass_rate
            total_mass_actual = dato.total_mass
            
            # Solo procesar si hay datos válidos
            if mass_rate_raw is None or total_mass_actual is None:
                continue
            
            registros_procesados += 1
            
            # Convertir a kg/min para verificar si hay flujo
            mass_rate_kg_min = lb_s_a_kg_min(mass_rate_raw)
            
            # Solo contar masa cuando HAY FLUJO (mass_rate > 0)
            if mass_rate_kg_min > 0:
                if masa_anterior is not None:
                    diferencia = total_mass_actual - masa_anterior
                    
                    # Detección de reset: Si la diferencia es negativa o muy grande
                    if diferencia < 0 or diferencia > 100000:  # 100,000 lb como límite razonable
                        # Hubo reset, reiniciar desde el valor actual
                        resets_detectados += 1
                        logger.info(
                            f"🔄 Reset #{resets_detectados} detectado en masa bruta: "
                            f"{masa_anterior:.2f} -> {total_mass_actual:.2f} lb en "
                            f"{dato.created_at_iot.astimezone(COLOMBIA_TZ)}"
                        )
                        masa_anterior = total_mass_actual
                    else:
                        # Acumulación normal
                        masa_acumulada_lb = diferencia
                        masa_acumulada_kg = lb_a_kg(masa_acumulada_lb)
                        masa_total_acumulada += masa_acumulada_kg
                        masa_anterior = total_mass_actual
                else:
                    # Primera lectura con flujo
                    logger.info(
                        f"🟢 Primera lectura con flujo: total_mass = {total_mass_actual:.2f} lb, "
                        f"mass_rate = {mass_rate_kg_min:.2f} kg/min"
                    )
                    masa_anterior = total_mass_actual
            # Si mass_rate <= 0, mantener última referencia (no actualizar masa_anterior)
        
        if resets_detectados > 0:
            logger.info(
                f"Masa total: {masa_total_acumulada:.2f} kg - {resets_detectados} resets detectados"
            )
        
        return masa_total_acumulada
