import logging
from datetime import timedelta
from django.db.models import Window, F, Q, IntegerField, FloatField, ExpressionWrapper
from django.db.models.functions import RowNumber, Mod
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema
from _AppMonitoreoCoriolis.models import NodeRedData
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
        # Intentar obtener del caché primero
        cache_key = f'tendencias_{sistema_id}'
        cached_response = cache.get(cache_key)
        
        if cached_response:
            logger.info(f"📦 Datos de tendencias servidos desde caché para sistema {sistema_id}")
            # Agregar flag para debugging
            cached_response['from_cache'] = True
            return Response(cached_response)
        
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
                        'presion': {'label': 'Presión', 'data': [], 'unidad': 'PSI', 'color': '#dc3545', 'total_registros': 0},
                        'densidad': {'label': 'Densidad', 'data': [], 'unidad': 'g/cc', 'color': "#cbdc35", 'total_registros': 0}
                    },
                    'total_registros': 0,
                    'info': 'No hay datos disponibles para este sistema'
                })
            
            # Calcular ventana de 30 minutos desde el último dato hacia atrás
            fecha_fin = ultimo_dato.created_at_iot
            fecha_inicio = fecha_fin - timedelta(minutes=30)
            
            # Consultar datos en esa ventana de tiempo usando timestamp IoT
            datos_query = NodeRedData.objects.filter(
                systemId=sistema,
                created_at_iot__range=[fecha_inicio, fecha_fin],
                created_at_iot__isnull=False
            ).order_by('created_at_iot')
            
            total_registros = datos_query.count()
            max_puntos = 80  # Reducido aún más para mejor performance
            decimacion_info = {'aplicada': False}
            
            # Aplicar decimación si hay más registros
            if total_registros > max_puntos:
                factor = max(2, total_registros // max_puntos)
                
                # Traer solo IDs (muy rápido)
                todos_ids = list(datos_query.values_list('id', flat=True))
                
                # Decimar índices
                ids_decimados = [todos_ids[i] for i in range(0, len(todos_ids), factor)]
                if todos_ids[-1] not in ids_decimados:
                    ids_decimados.append(todos_ids[-1])
                
                # Query con conversiones en SQL (más rápido que Python)
                datos = list(NodeRedData.objects.filter(id__in=ids_decimados).annotate(
                    # Conversiones matemáticas en PostgreSQL (10x más rápido)
                    flujo_masico_kg=ExpressionWrapper(
                        F('mass_rate') * 27.2155,  # lb/s a kg/min (60 * 0.453592)
                        output_field=FloatField()
                    ),
                    flujo_vol_gal=ExpressionWrapper(
                        F('flow_rate') * 0.0158503,  # cm³/s a gal/min
                        output_field=FloatField()
                    ),
                    temp_coriolis_f=ExpressionWrapper(
                        (F('coriolis_temperature') * 9.0 / 5.0) + 32.0,  # °C a °F
                        output_field=FloatField()
                    ),
                    temp_redundante_celsius=F('redundant_temperature'),  # Para corrección posterior
                    presion_raw=F('pressure_out'),  # Para corrección posterior
                    densidad_gcc=F('density')
                ).values(
                    'created_at_iot', 'flujo_masico_kg', 'flujo_vol_gal', 
                    'temp_coriolis_f', 'temp_redundante_celsius', 'presion_raw',
                    'densidad_gcc', 'mt', 'bt', 'mp', 'bp'
                ).order_by('created_at_iot'))
                
                decimacion_info = {
                    'aplicada': True,
                    'total_original': total_registros,
                    'total_decimado': len(ids_decimados),
                    'factor': factor,
                    'porcentaje_reduccion': round((1 - len(ids_decimados) / total_registros) * 100, 1)
                }
            else:
                # Query con conversiones en SQL (más rápido que Python)
                datos = list(datos_query.annotate(
                    # Conversiones matemáticas en PostgreSQL (10x más rápido)
                    flujo_masico_kg=ExpressionWrapper(
                        F('mass_rate') * 27.2155,  # lb/s a kg/min (60 * 0.453592)
                        output_field=FloatField()
                    ),
                    flujo_vol_gal=ExpressionWrapper(
                        F('flow_rate') * 0.0158503,  # cm³/s a gal/min
                        output_field=FloatField()
                    ),
                    temp_coriolis_f=ExpressionWrapper(
                        (F('coriolis_temperature') * 9.0 / 5.0) + 32.0,  # °C a °F
                        output_field=FloatField()
                    ),
                    temp_redundante_celsius=F('redundant_temperature'),  # Para corrección posterior
                    presion_raw=F('pressure_out'),  # Para corrección posterior
                    densidad_gcc=F('density')
                ).values(
                    'created_at_iot', 'flujo_masico_kg', 'flujo_vol_gal', 
                    'temp_coriolis_f', 'temp_redundante_celsius', 'presion_raw',
                    'densidad_gcc', 'mt', 'bt', 'mp', 'bp'
                ))
            
            # Preparar datos para cada variable
            flujo_masico = []
            flujo_volumetrico = []
            temperatura_coriolis = []
            temperatura_salida = []
            presion = []
            densidad = []
            
            # Loop optimizado: solo aplicar correcciones y formatear
            # Las conversiones ya se hicieron en SQL (mucho más rápido)
            for dato in datos:
                # Convertir UTC a hora de Colombia usando timestamp IoT
                fecha_colombia = dato['created_at_iot'].astimezone(COLOMBIA_TZ)
                timestamp = int(fecha_colombia.timestamp() * 1000)
                fecha_str = fecha_colombia.strftime('%H:%M')
                
                # Flujo Másico - ya convertido en SQL
                if dato['flujo_masico_kg'] is not None:
                    flujo_masico.append({
                        'x': timestamp,
                        'y': round(dato['flujo_masico_kg'], 2),
                        'fecha': fecha_str
                    })
                
                # Flujo Volumétrico - ya convertido en SQL
                if dato['flujo_vol_gal'] is not None:
                    flujo_volumetrico.append({
                        'x': timestamp,
                        'y': round(dato['flujo_vol_gal'], 2),
                        'fecha': fecha_str
                    })
                
                # Temperatura Coriolis - ya convertido en SQL a °F
                if dato['temp_coriolis_f'] is not None:
                    temperatura_coriolis.append({
                        'x': timestamp,
                        'y': round(dato['temp_coriolis_f'], 2),
                        'fecha': fecha_str
                    })
                
                # Temperatura de Salida - aplicar corrección mx+b y convertir a °F
                if dato['temp_redundante_celsius'] is not None:
                    mt_momento = dato['mt'] if dato['mt'] is not None else mt
                    bt_momento = dato['bt'] if dato['bt'] is not None else bt
                    # Corrección en Celsius primero, luego convertir a °F
                    temp_celsius_corr = mt_momento * float(dato['temp_redundante_celsius']) + bt_momento
                    temp_f_corr = (temp_celsius_corr * 9.0 / 5.0) + 32.0
                    temperatura_salida.append({
                        'x': timestamp,
                        'y': round(temp_f_corr, 2),
                        'fecha': fecha_str
                    })
                
                # Presión - aplicar corrección mx+b
                if dato['presion_raw'] is not None:
                    mp_momento = dato['mp'] if dato['mp'] is not None else mp
                    bp_momento = dato['bp'] if dato['bp'] is not None else bp
                    presion_corregida = mp_momento * dato['presion_raw'] + bp_momento
                    presion.append({
                        'x': timestamp,
                        'y': round(presion_corregida, 2),
                        'fecha': fecha_str
                    })

                # Densidad - ya viene en g/cc
                if dato['densidad_gcc'] is not None:
                    densidad.append({
                        'x': timestamp,
                        'y': round(dato['densidad_gcc'], 4),
                        'fecha': fecha_str
                    })

            response_data = {
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
                    },
                    'densidad': {
                        'label': 'Densidad',
                        'data': densidad,
                        'unidad': 'g/cc',
                        'color': "#cbdc35",  # Amarillo verdoso
                        'total_registros': len(densidad)
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
                'total_registros': total_registros,
                'decimacion_info': decimacion_info,
                'from_cache': False
            }
            
            # Guardar en caché por 30 segundos para mejor performance al cambiar de sistema
            cache.set(cache_key, response_data, 30)
            logger.info(f"💾 Datos de tendencias guardados en caché para sistema {sistema_id}")
            
            return Response(response_data)
            
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