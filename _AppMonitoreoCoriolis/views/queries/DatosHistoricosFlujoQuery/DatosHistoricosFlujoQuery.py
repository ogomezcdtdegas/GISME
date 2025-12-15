from django.utils import timezone
from datetime import timedelta, datetime
import pytz
import logging
from django.db.models import Window, F, Q, IntegerField
from django.db.models.functions import RowNumber, Mod
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema
from _AppMonitoreoCoriolis.models import NodeRedData
from UTIL_LIB.conversiones import cm3_s_a_gal_min, lb_s_a_kg_min
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ
from _AppMonitoreoCoriolis.views.utils_decimation import calcular_estadisticas_decimacion

# Configurar logging
logger = logging.getLogger(__name__)

class DatosHistoricosFlujoQueryView(APIView):
    """
    CBV para obtener datos históricos de flujo (volumétrico y másico) para un sistema específico
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            # Logging para debug
            logger.info(f"DatosHistoricosFlujoQueryView - Sistema ID: {sistema_id}")
            logger.info(f"Query params: {dict(request.GET)}")
            
            # Verificar que el sistema existe
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener parámetros de fecha
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            tiempo_real = request.GET.get('tiempo_real', 'false').lower() == 'true'
            horas_atras = float(request.GET.get('horas_atras', '4'))  # Por defecto 4 horas
            
            logger.info(f"Fechas recibidas - Inicio: {fecha_inicio}, Fin: {fecha_fin}, Tiempo Real: {tiempo_real}")
            
            # MODO TIEMPO REAL: Calcular desde el último dato disponible
            if tiempo_real:
                ultimo_dato = NodeRedData.objects.filter(systemId=sistema).order_by('-created_at_iot').first()
                
                if ultimo_dato and ultimo_dato.created_at_iot:
                    # Usar el created_at_iot del último dato como fecha_fin
                    fecha_fin = ultimo_dato.created_at_iot
                    fecha_inicio = fecha_fin - timedelta(hours=horas_atras)
                    logger.info(f"Modo Tiempo Real - Último dato: {fecha_fin}, Inicio calculado: {fecha_inicio}")
                else:
                    # Si no hay datos, usar fecha actual
                    fecha_fin = timezone.now()
                    fecha_inicio = fecha_fin - timedelta(hours=horas_atras)
                    logger.info(f"No hay datos previos. Usando fechas por defecto - Inicio: {fecha_inicio}, Fin: {fecha_fin}")
            # Si no se especifican fechas, usar últimos 7 días
            elif not fecha_inicio or not fecha_fin:
                fecha_fin = timezone.now()
                fecha_inicio = fecha_fin - timedelta(days=7)
                logger.info(f"Using default dates - Inicio: {fecha_inicio}, Fin: {fecha_fin}")
            else:
                # Parsear fechas con formato datetime y establecer timezone de Colombia
                try:
                    # Intentar formato con fecha y hora: "2025-09-17T21:31:00"
                    fecha_inicio_naive = datetime.strptime(fecha_inicio, '%Y-%m-%dT%H:%M:%S')
                    fecha_fin_naive = datetime.strptime(fecha_fin, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    try:
                        # Fallback a formato solo fecha: "2025-09-17"
                        fecha_inicio_naive = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                        fecha_fin_naive = datetime.strptime(fecha_fin, '%Y-%m-%d')
                        
                        # Establecer horas para cubrir todo el rango del día
                        fecha_inicio_naive = fecha_inicio_naive.replace(hour=0, minute=0, second=0, microsecond=0)
                        fecha_fin_naive = fecha_fin_naive.replace(hour=23, minute=59, second=59, microsecond=999999)
                    except ValueError:
                        return Response({
                            'success': False,
                            'error': 'Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS'
                        })
                
                # Asumir que las fechas del frontend están en hora de Colombia y convertir a UTC
                fecha_inicio = COLOMBIA_TZ.localize(fecha_inicio_naive).astimezone(pytz.UTC)
                fecha_fin = COLOMBIA_TZ.localize(fecha_fin_naive).astimezone(pytz.UTC)
                
                logger.info(f"Fechas convertidas a UTC - Inicio: {fecha_inicio}, Fin: {fecha_fin}")
            
            # Consultar datos usando created_at_iot (timestamp del dispositivo IoT)
            logger.info(f"Consultando datos para sistema: {sistema.tag}")
            datos_query = NodeRedData.objects.filter(
                systemId=sistema,
                created_at_iot__gte=fecha_inicio,
                created_at_iot__lte=fecha_fin,
                created_at_iot__isnull=False
            ).order_by('created_at_iot')
            
            total_registros = datos_query.count()
            logger.info(f"Datos encontrados: {total_registros} registros")
            
            # Aplicar decimación SQL si hay más de 2000 registros
            max_puntos = 2000
            decimacion_info = {'aplicada': False}
            
            if total_registros > max_puntos:
                factor = max(1, total_registros // max_puntos)
                logger.info(f"🔍 Aplicando decimación SQL: factor {factor} (tomar 1 de cada {factor})")
                
                # Obtener IDs decimados
                ids_decimados = datos_query.annotate(
                    row_num=Window(
                        expression=RowNumber(),
                        order_by=F('created_at_iot').asc()
                    ),
                    row_mod=Mod(
                        Window(
                            expression=RowNumber(),
                            order_by=F('created_at_iot').asc()
                        ),
                        factor,
                        output_field=IntegerField()
                    )
                ).filter(
                    Q(row_num=1) |
                    Q(row_num=total_registros) |
                    Q(row_mod=0)
                ).values_list('id', flat=True)
                
                # Obtener objetos limpios
                datos = list(NodeRedData.objects.filter(id__in=list(ids_decimados)).order_by('created_at_iot'))
                stats = calcular_estadisticas_decimacion(total_registros, len(datos))
                decimacion_info = {
                    'aplicada': True,
                    'total_original': total_registros,
                    'total_decimado': len(datos),
                    'factor_reduccion': stats['factor_reduccion'],
                    'porcentaje_reduccion': stats['porcentaje_reduccion']
                }
                logger.info(f"✅ Decimación aplicada: {len(datos)} registros ({stats['porcentaje_reduccion']:.1f}% reducción)")
            else:
                datos = list(datos_query)
                logger.info(f"ℹ️ Sin decimación: {total_registros} registros")
            
            # Preparar datos para ambos flujos
            flujo_volumetrico = []
            flujo_masico = []
            
            for dato in datos:
                # Convertir UTC a hora de Colombia usando created_at_iot
                fecha_colombia = dato.created_at_iot.astimezone(COLOMBIA_TZ)
                timestamp = int(fecha_colombia.timestamp() * 1000)
                fecha_str = fecha_colombia.strftime('%d/%m %H:%M')
                
                # Flujo volumétrico - convertir a gal/min
                if dato.flow_rate is not None:
                    valor_convertido = cm3_s_a_gal_min(float(dato.flow_rate))
                    flujo_volumetrico.append({
                        'fecha': fecha_str,
                        'valor': valor_convertido,
                        'timestamp': timestamp
                    })
                
                # Flujo másico - convertir a kg/min
                if dato.mass_rate is not None:
                    valor_convertido = lb_s_a_kg_min(float(dato.mass_rate))
                    flujo_masico.append({
                        'fecha': fecha_str,
                        'valor': valor_convertido,
                        'timestamp': timestamp
                    })
            
            return Response({
                'success': True,
                'flujo_volumetrico': {
                    'datos': flujo_volumetrico,
                    'unidad': 'gal/min',
                    'total_registros': len(flujo_volumetrico)
                },
                'flujo_masico': {
                    'datos': flujo_masico,
                    'unidad': 'kg/min',
                    'total_registros': len(flujo_masico)
                },
                'decimacion_info': decimacion_info,
                'sistema': {
                    'id': str(sistema.id),
                    'tag': sistema.tag,
                    'sistema_id': sistema.sistema_id
                },
                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin.strftime('%Y-%m-%d')
            })
            
        except Sistema.DoesNotExist:
            logger.error(f"Sistema no encontrado: {sistema_id}")
            return Response({
                'success': False,
                'error': 'Sistema no encontrado'
            }, status=404)
        except Exception as e:
            logger.error(f"Error en DatosHistoricosFlujoQueryView: {str(e)}", exc_info=True)
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Args del error: {e.args}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)