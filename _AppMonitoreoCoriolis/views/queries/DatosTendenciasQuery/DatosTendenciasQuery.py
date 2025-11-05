import logging
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema
from _AppMonitoreoCoriolis.models import NodeRedData
from UTIL_LIB.conversiones import celsius_a_fahrenheit, cm3_s_a_gal_min, lb_s_a_kg_min
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ, get_coeficientes_correccion, convertir_presion_con_span

# Configurar logging
logger = logging.getLogger(__name__)

class DatosTendenciasQueryView(APIView):
    """
    CBV para obtener datos de tendencias de las últimas 4 horas para el gráfico
    Incluye: Flujo Másico, Flujo Volumétrico, Temperatura Coriolis, Temperatura de Salida y Presión
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener coeficientes de corrección
            mt, bt, mp, bp, span_presion, zero_presion = get_coeficientes_correccion(sistema)
            
            # Obtener el último dato disponible para establecer el punto de referencia
            ultimo_dato = NodeRedData.objects.filter(
                systemId=sistema,
                created_at_iot__isnull=False
            ).order_by('-created_at_iot').first()
            
            if not ultimo_dato:
                return Response({
                    'success': True,
                    'datasets': {
                        'flujo_masico': {'label': 'Flujo Másico', 'data': [], 'unidad': 'kg/min', 'color': '#28a745', 'total_registros': 0},
                        'flujo_volumetrico': {'label': 'Flujo Volumétrico', 'data': [], 'unidad': 'm³/min', 'color': '#007bff', 'total_registros': 0},
                        'temperatura_coriolis': {'label': 'Temperatura Coriolis', 'data': [], 'unidad': '°F', 'color': '#f59416', 'total_registros': 0},
                        'temperatura_salida': {'label': 'Temperatura de Salida', 'data': [], 'unidad': '°F', 'color': '#6f42c1', 'total_registros': 0},
                        'presion': {'label': 'Presión', 'data': [], 'unidad': 'PSI', 'color': '#dc3545', 'total_registros': 0}
                    },
                    'total_registros': 0,
                    'info': 'No hay datos disponibles para este sistema'
                })
            
            # Calcular ventana de 30 minutos desde el último dato hacia atrás
            fecha_fin = ultimo_dato.created_at_iot
            fecha_inicio = fecha_fin - timedelta(minutes=30)
            
            # Consultar datos en esa ventana de tiempo usando timestamp IoT
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at_iot__range=[fecha_inicio, fecha_fin],
                created_at_iot__isnull=False
            ).order_by('created_at_iot')
            
            # Preparar datos para cada variable
            flujo_masico = []
            flujo_volumetrico = []
            temperatura_coriolis = []
            temperatura_salida = []
            presion = []
            
            for dato in datos:
                # Convertir UTC a hora de Colombia usando timestamp IoT
                fecha_colombia = dato.created_at_iot.astimezone(COLOMBIA_TZ)
                timestamp = int(fecha_colombia.timestamp() * 1000)
                fecha_str = fecha_colombia.strftime('%H:%M')
                
                # Flujo Másico - convertir a kg/min
                if dato.mass_rate is not None:
                    valor_convertido = lb_s_a_kg_min(float(dato.mass_rate))
                    flujo_masico.append({
                        'x': timestamp,
                        'y': valor_convertido,
                        'fecha': fecha_str
                    })
                
                # Flujo Volumétrico - convertir a gal/min
                if dato.flow_rate is not None:
                    valor_convertido = cm3_s_a_gal_min(float(dato.flow_rate))
                    flujo_volumetrico.append({
                        'x': timestamp,
                        'y': valor_convertido,
                        'fecha': fecha_str
                    })
                
                # Temperatura Coriolis - convertir a °F
                if dato.coriolis_temperature is not None:
                    valor_convertido = celsius_a_fahrenheit(float(dato.coriolis_temperature))
                    temperatura_coriolis.append({
                        'x': timestamp,
                        'y': valor_convertido,
                        'fecha': fecha_str
                    })
                
                # Temperatura de Salida (redundant_temperature) - APLICAR CORRECCIÓN DEL MOMENTO y convertir a °F
                if dato.redundant_temperature is not None:
                    # Usar coeficientes del momento si están disponibles, sino usar los actuales
                    mt_momento = dato.mt if dato.mt is not None else mt
                    bt_momento = dato.bt if dato.bt is not None else bt
                    temp_corregida = mt_momento * float(dato.redundant_temperature) + bt_momento
                    valor_convertido = celsius_a_fahrenheit(temp_corregida)
                    temperatura_salida.append({
                        'x': timestamp,
                        'y': valor_convertido,
                        'fecha': fecha_str
                    })
                
                # Presión - APLICAR CORRECCIÓN DEL MOMENTO y mantener en PSI
                if dato.pressure_out is not None:
                    # 1. Convertir valor crudo con span
                    valor_convertido = convertir_presion_con_span(dato.pressure_out, span_presion)
                    
                    # 2. Aplicar corrección mx+b del momento
                    # Usar coeficientes del momento si están disponibles, sino usar los actuales
                    mp_momento = dato.mp if dato.mp is not None else mp
                    bp_momento = dato.bp if dato.bp is not None else bp
                    presion_corregida = mp_momento * valor_convertido + bp_momento
                    presion.append({
                        'x': timestamp,
                        'y': presion_corregida,
                        'fecha': fecha_str
                    })
            
            return Response({
                'success': True,
                'datasets': {
                    'flujo_masico': {
                        'label': 'Flujo Másico',
                        'data': flujo_masico,
                        'unidad': 'kg/min',
                        'color': '#28a745',  # Verde
                        'total_registros': len(flujo_masico)
                    },
                    'flujo_volumetrico': {
                        'label': 'Flujo Volumétrico',
                        'data': flujo_volumetrico,
                        'unidad': 'gal/min',
                        'color': '#007bff',  # Azul
                        'total_registros': len(flujo_volumetrico)
                    },
                    'temperatura_coriolis': {
                        'label': 'Temperatura Coriolis',
                        'data': temperatura_coriolis,
                        'unidad': '°F',
                        'color': '#f59416',  # Naranja
                        'total_registros': len(temperatura_coriolis)
                    },
                    'temperatura_salida': {
                        'label': 'Temperatura de Salida',
                        'data': temperatura_salida,
                        'unidad': '°F',
                        'color': '#6f42c1',  # Púrpura
                        'total_registros': len(temperatura_salida)
                    },
                    'presion': {
                        'label': 'Presión',
                        'data': presion,
                        'unidad': 'PSI',
                        'color': '#dc3545',  # Rojo
                        'total_registros': len(presion)
                    }
                },
                'sistema': {
                    'id': str(sistema.id),
                    'tag': sistema.tag,
                    'sistema_id': sistema.sistema_id
                },
                'periodo': '30 minutos desde último dato',
                'ventana_tiempo': {
                    'inicio': fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%H:%M'),
                    'fin': fecha_fin.astimezone(COLOMBIA_TZ).strftime('%H:%M'),
                    'ultimo_dato': ultimo_dato.created_at_iot.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S')
                },
                'timestamp': fecha_fin.isoformat(),
                'total_registros': datos.count()
            })
            
        except Sistema.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Sistema no encontrado'
            }, status=404)
        except Exception as e:
            logger.error(f"Error en DatosTendenciasQueryView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)