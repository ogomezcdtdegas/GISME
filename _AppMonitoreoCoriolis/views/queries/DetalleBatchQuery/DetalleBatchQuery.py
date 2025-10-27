import logging
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import ConfiguracionCoeficientes
from _AppMonitoreoCoriolis.models import NodeRedData, BatchDetectado
from UTIL_LIB.conversiones import celsius_a_fahrenheit, lb_s_a_kg_min, lb_a_kg
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ

# Configurar logging
logger = logging.getLogger(__name__)

class DetalleBatchQueryView(APIView):
    """
    CBV para obtener el detalle de un batch específico con datos para graficar
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, batch_id):
        try:
            # Obtener el batch
            batch = get_object_or_404(BatchDetectado, id=batch_id)
            
            # Obtener configuración para los límites del flujo másico
            try:
                config = ConfiguracionCoeficientes.objects.get(systemId=batch.systemId)
                lim_inf = config.lim_inf_caudal_masico or 0  # En kg/min
                lim_sup = config.lim_sup_caudal_masico or 9999  # En kg/min
            except ConfiguracionCoeficientes.DoesNotExist:
                lim_inf = 0
                lim_sup = 9999
            
            # Extender el rango de datos 3 minutos antes y después para mejor contexto visual
            inicio_extendido = batch.fecha_inicio - timedelta(minutes=3)
            fin_extendido = batch.fecha_fin + timedelta(minutes=3)
            
            # Obtener todos los datos del intervalo extendido del batch
            datos = NodeRedData.objects.filter(
                systemId=batch.systemId,
                created_at_iot__gte=inicio_extendido,
                created_at_iot__lte=fin_extendido,
                created_at_iot__isnull=False  # Solo datos con timestamp IoT válido
            ).order_by('created_at_iot')
            
            if not datos.exists():
                return Response({
                    'success': False,
                    'error': 'No se encontraron datos para este batch'
                }, status=404)
            
            # Preparar datos para el gráfico
            datos_grafico = []
            for dato in datos:
                # Convertir UTC a hora de Colombia usando timestamp IoT
                fecha_colombia = dato.created_at_iot.astimezone(COLOMBIA_TZ)
                
                # Determinar si el punto está dentro del batch real o en el contexto extendido
                dentro_batch = batch.fecha_inicio <= dato.created_at_iot <= batch.fecha_fin
                
                # Convertir mass_rate de lb/sec a kg/min para consistencia
                mass_rate_kg_min = lb_s_a_kg_min(dato.mass_rate) if dato.mass_rate is not None else None
                
                # Convertir total_mass de lb a kg
                total_mass_kg = lb_a_kg(dato.total_mass) if dato.total_mass is not None else None
                
                # Convertir temperatura de °C a °F
                temperatura_f = celsius_a_fahrenheit(dato.coriolis_temperature) if dato.coriolis_temperature is not None else None
                
                datos_grafico.append({
                    'timestamp': int(fecha_colombia.timestamp() * 1000),  # Para Chart.js
                    'fecha_hora': fecha_colombia.strftime('%d/%m %H:%M:%S'),
                    'mass_rate_lb_s': dato.mass_rate,  # Original en lb/s
                    'mass_rate_kg_min': mass_rate_kg_min,  # Convertido a kg/min
                    'total_mass_lb': dato.total_mass,  # Original en lb
                    'total_mass_kg': total_mass_kg,  # Convertido a kg
                    'coriolis_temperature_c': dato.coriolis_temperature,  # Original en °C
                    'coriolis_temperature_f': temperatura_f,  # Convertido a °F
                    'density': dato.density,
                    'dentro_batch': dentro_batch  # Indica si está dentro del batch real
                })
            
            return Response({
                'success': True,
                'batch_info': {
                    'id': batch.id,
                    'sistema_tag': batch.systemId.tag,
                    'fecha_inicio': batch.fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin': batch.fecha_fin.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'mass_total_kg': batch.mass_total,
                    'vol_total': batch.vol_total,
                    'presion_out_prom': batch.pressure_out_prom,
                    'temperatura_coriolis_prom_c': batch.temperatura_coriolis_prom,  # Original en °C
                    'temperatura_coriolis_prom_f': celsius_a_fahrenheit(batch.temperatura_coriolis_prom) if batch.temperatura_coriolis_prom is not None else None,  # Convertido a °F
                    'densidad_prom': batch.densidad_prom,
                    'duracion_minutos': batch.duracion_minutos,
                    'total_registros': batch.total_registros,
                    # Timestamps para marcar límites del batch en la gráfica
                    'timestamp_inicio': int(batch.fecha_inicio.astimezone(COLOMBIA_TZ).timestamp() * 1000),
                    'timestamp_fin': int(batch.fecha_fin.astimezone(COLOMBIA_TZ).timestamp() * 1000)
                },
                'datos_grafico': datos_grafico,
                'total_datos': len(datos_grafico),
                # Límites para las líneas horizontales en el gráfico
                'lim_inf_caudal_masico': lim_inf,
                'lim_sup_caudal_masico': lim_sup
            })
            
        except Exception as e:
            logger.error(f"Error en DetalleBatchQueryView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error al obtener detalle del batch: {str(e)}'
            }, status=500)