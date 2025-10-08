from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta, datetime
import pytz
import logging
from .models import NodeRedData, BatchDetectado
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes
from UTIL_LIB.conversiones import (
    celsius_a_fahrenheit, 
    lb_s_a_kg_min, 
    lb_a_kg,  # Nueva para convertir masa total
    cm3_s_a_m3_min,  # Mantenida aunque no se use
    cm3_s_a_gal_min,  # Nueva para flujo volumétrico
    cm3_a_m3,  # Mantenida aunque no se use
    cm3_a_gal,  # Nueva para volumen total
    lb_a_kg,
    formatear_numero
)

# Configurar logging
logger = logging.getLogger(__name__)

# Configurar zona horaria de Colombia
COLOMBIA_TZ = pytz.timezone('America/Bogota')

# Función utilitaria para obtener coeficientes de corrección
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

# Función utilitaria para convertir presión con span
def convertir_presion_con_span(valor_crudo, span_presion):
    """
    Convierte el valor crudo de presión usando el span del sistema.
    Formula: (span_presion / 4095) * valor_crudo
    Si span_presion es None o 0, retorna el valor crudo sin conversión.
    """
    if valor_crudo is None:
        return None
    
    if span_presion is None or span_presion == 0:
        # Si no hay span configurado, usar el valor crudo directamente
        return float(valor_crudo)
    
    return (float(span_presion) / 4095.0) * float(valor_crudo)

# Vista base para SPA - Solo renderiza el template principal
class MonitoreoCoriolisBaseView(LoginRequiredMixin, TemplateView):
    """Vista base SPA que renderiza el template principal con JavaScript"""
    template_name = '_AppMonitoreoCoriolis/coriolis_spa.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'monitoreo_coriolis'
        return context

# Vista para sistema específico
class MonitoreoCoriolisSistemaView(LoginRequiredMixin, TemplateView):
    """Vista CBV para mostrar detalles específicos de un sistema"""
    template_name = '_AppMonitoreoCoriolis/coriolis_spa.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sistema = get_object_or_404(Sistema, id=kwargs['sistema_id'])
        context.update({
            'sistema': sistema,
            'active_section': 'monitoreo_coriolis'
        })
        return context

# ===== APIS PARA DATOS HISTORICOS CON CBV =====

class DatosHistoricosFlujoView(APIView):
    """
    CBV para obtener datos históricos de flujo (volumétrico y másico) para un sistema específico
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            # Logging para debug
            logger.info(f"DatosHistoricosFlujoView - Sistema ID: {sistema_id}")
            logger.info(f"Query params: {dict(request.GET)}")
            
            # Verificar que el sistema existe
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener parámetros de fecha
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            logger.info(f"Fechas recibidas - Inicio: {fecha_inicio}, Fin: {fecha_fin}")
            
            # Si no se especifican fechas, usar últimos 7 días
            if not fecha_inicio or not fecha_fin:
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
            
            # Consultar datos
            logger.info(f"Consultando datos para sistema: {sistema.tag}")
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at__range=[fecha_inicio, fecha_fin]
            ).order_by('created_at')
            
            logger.info(f"Datos encontrados: {datos.count()} registros")
            
            # Preparar datos para ambos flujos
            flujo_volumetrico = []
            flujo_masico = []
            
            for dato in datos:
                # Convertir UTC a hora de Colombia
                fecha_colombia = dato.created_at.astimezone(COLOMBIA_TZ)
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
            logger.error(f"Error en DatosHistoricosFlujoView: {str(e)}", exc_info=True)
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Args del error: {e.args}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)

class DatosHistoricosPresionView(APIView):
    """
    CBV para obtener datos históricos de presión para un sistema específico
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            # Logging para debug
            logger.info(f"DatosHistoricosPresionView - Sistema ID: {sistema_id}")
            logger.info(f"Query params: {dict(request.GET)}")
            
            # Verificar que el sistema existe
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener coeficientes de corrección
            mt, bt, mp, bp, span_presion, zero_presion = get_coeficientes_correccion(sistema)
            
            # Obtener parámetros de fecha
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            logger.info(f"Fechas recibidas - Inicio: {fecha_inicio}, Fin: {fecha_fin}")
            
            # Si no se especifican fechas, usar últimos 7 días
            if not fecha_inicio or not fecha_fin:
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
            
            # Consultar datos
            logger.info(f"Consultando datos de presión para sistema: {sistema.tag}")
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at__range=[fecha_inicio, fecha_fin]
            ).order_by('created_at')
            
            logger.info(f"Datos encontrados: {datos.count()} registros")
            
            # Verificar si se solicita exportación CSV
            export_format = request.GET.get('export')
            if export_format == 'csv':
                return self._exportar_csv_presion(datos, sistema, fecha_inicio, fecha_fin)
            
            # Preparar datos de presión
            datos_presion = []
            
            for dato in datos:
                # Convertir UTC a hora de Colombia
                fecha_colombia = dato.created_at.astimezone(COLOMBIA_TZ)
                timestamp = int(fecha_colombia.timestamp() * 1000)
                fecha_str = fecha_colombia.strftime('%d/%m %H:%M')
                
                # Usar pressure_out con corrección del momento aplicada
                if dato.pressure_out is not None:
                    # 1. Convertir valor crudo con span
                    valor_convertido = convertir_presion_con_span(dato.pressure_out, span_presion)
                    
                    # 2. Aplicar corrección mx+b
                    # Usar coeficientes del momento (mp, bp) si están disponibles, sino usar los actuales
                    mp_momento = dato.mp if dato.mp is not None else mp
                    bp_momento = dato.bp if dato.bp is not None else bp
                    presion_corregida = mp_momento * valor_convertido + bp_momento
                    datos_presion.append({
                        'fecha': fecha_str,
                        'valor': presion_corregida,
                        'timestamp': timestamp
                    })
            
            return Response({
                'success': True,
                'datos': datos_presion,
                'unidad': 'PSI',
                'total_registros': len(datos_presion),
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
            logger.error(f"Error en DatosHistoricosPresionView: {str(e)}", exc_info=True)
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Args del error: {e.args}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
    
    def _exportar_csv_presion(self, datos, sistema, fecha_inicio, fecha_fin):
        """Exportar datos de presión como CSV"""
        from django.http import HttpResponse
        import csv
        
        # Obtener coeficientes de corrección
        mt, bt, mp, bp = get_coeficientes_correccion(sistema)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="presion_{sistema.tag}_{fecha_inicio.strftime("%Y%m%d")}_{fecha_fin.strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Hora', 'Presión (PSI)', 'Sistema'])
        
        for dato in datos:
            if dato.pressure_out is not None:
                fecha_colombia = dato.created_at.astimezone(COLOMBIA_TZ)
                # Usar coeficientes del momento si están disponibles, sino usar los actuales
                mp_momento = dato.mp if dato.mp is not None else mp
                bp_momento = dato.bp if dato.bp is not None else bp
                presion_corregida = mp_momento * float(dato.pressure_out) + bp_momento
                writer.writerow([
                    fecha_colombia.strftime('%d/%m/%Y'),
                    fecha_colombia.strftime('%H:%M:%S'),
                    presion_corregida,
                    sistema.tag
                ])
        
        return response

class DatosHistoricosTemperaturaView(APIView):
    """
    CBV para obtener datos históricos de temperatura para un sistema específico
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            # Logging para debug
            logger.info(f"DatosHistoricosTemperaturaView - Sistema ID: {sistema_id}")
            logger.info(f"Query params: {dict(request.GET)}")
            
            # Verificar que el sistema existe
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener coeficientes de corrección
            mt, bt, mp, bp, span_presion, zero_presion = get_coeficientes_correccion(sistema)
            
            # Obtener parámetros de fecha
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            export = request.GET.get('export')
            
            logger.info(f"Fechas recibidas - Inicio: {fecha_inicio}, Fin: {fecha_fin}")
            
            # Si no se especifican fechas, usar últimos 7 días
            if not fecha_inicio or not fecha_fin:
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
            
            logger.info(f"Fechas UTC para consulta - Inicio: {fecha_inicio}, Fin: {fecha_fin}")
            
            # Consultar datos de temperatura del sistema
            datos_query = NodeRedData.objects.filter(
                systemId=sistema,
                created_at__gte=fecha_inicio,
                created_at__lte=fecha_fin
            ).order_by('created_at')
            
            logger.info(f"Query generada: {datos_query.query}")
            logger.info(f"Total de registros encontrados: {datos_query.count()}")
            
            # Si es exportación CSV, retornar CSV
            if export == 'csv':
                return self._exportar_csv_temperatura(datos_query, sistema, fecha_inicio, fecha_fin)
            
            # Preparar datos para gráficos separados
            datos_coriolis = []
            datos_diagnostic = []
            datos_redundant = []
            
            for dato in datos_query:
                # Convertir timestamp a hora de Colombia para mostrar
                fecha_colombia = dato.created_at.astimezone(COLOMBIA_TZ)
                fecha_str = fecha_colombia.strftime('%d/%m/%Y %H:%M:%S')
                timestamp = fecha_colombia.isoformat()
                
                # Temperatura Coriolis - convertir a °F
                if dato.coriolis_temperature is not None:
                    valor_convertido = celsius_a_fahrenheit(float(dato.coriolis_temperature))
                    datos_coriolis.append({
                        'fecha': fecha_str,
                        'valor': valor_convertido,
                        'timestamp': timestamp
                    })
                
                # Temperatura Diagnóstico - convertir a °F
                if dato.diagnostic_temperature is not None:
                    valor_convertido = celsius_a_fahrenheit(float(dato.diagnostic_temperature))
                    datos_diagnostic.append({
                        'fecha': fecha_str,
                        'valor': valor_convertido,
                        'timestamp': timestamp
                    })
                
                # Temperatura Redundante (Temperatura de Salida) - APLICAR CORRECCIÓN DEL MOMENTO y convertir a °F
                if dato.redundant_temperature is not None:
                    # Usar coeficientes del momento (mt, bt) si están disponibles, sino usar los actuales
                    mt_momento = dato.mt if dato.mt is not None else mt
                    bt_momento = dato.bt if dato.bt is not None else bt
                    temp_corregida = mt_momento * float(dato.redundant_temperature) + bt_momento
                    valor_convertido = celsius_a_fahrenheit(temp_corregida)
                    datos_redundant.append({
                        'fecha': fecha_str,
                        'valor': valor_convertido,
                        'timestamp': timestamp
                    })
            
            return Response({
                'success': True,
                'coriolis_temperature': {
                    'datos': datos_coriolis,
                    'total_registros': len(datos_coriolis),
                    'unidad': '°F'
                },
                'diagnostic_temperature': {
                    'datos': datos_diagnostic,
                    'total_registros': len(datos_diagnostic),
                    'unidad': '°F'
                },
                'redundant_temperature': {
                    'datos': datos_redundant,
                    'total_registros': len(datos_redundant),
                    'unidad': '°F'
                },
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
            logger.error(f"Error en DatosHistoricosTemperaturaView: {str(e)}", exc_info=True)
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Args del error: {e.args}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
    
    def _exportar_csv_temperatura(self, datos, sistema, fecha_inicio, fecha_fin):
        """Exportar datos de temperatura como CSV"""
        from django.http import HttpResponse
        import csv
        
        # Obtener coeficientes de corrección
        mt, bt, mp, bp = get_coeficientes_correccion(sistema)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="temperatura_{sistema.tag}_{fecha_inicio.strftime("%Y%m%d")}_{fecha_fin.strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Hora', 'Temp. Coriolis (°C)', 'Temp. Diagnóstico (°C)', 'Temp. Redundante (°C)', 'Sistema'])
        
        for dato in datos:
            fecha_colombia = dato.created_at.astimezone(COLOMBIA_TZ)
            
            # Aplicar corrección del momento a temperatura redundante (temperatura de salida)
            temp_redundante_corregida = None
            if dato.redundant_temperature is not None:
                # Usar coeficientes del momento si están disponibles, sino usar los actuales
                mt_momento = dato.mt if dato.mt is not None else mt
                bt_momento = dato.bt if dato.bt is not None else bt
                temp_redundante_corregida = mt_momento * float(dato.redundant_temperature) + bt_momento
            
            writer.writerow([
                fecha_colombia.strftime('%d/%m/%Y'),
                fecha_colombia.strftime('%H:%M:%S'),
                float(dato.coriolis_temperature) if dato.coriolis_temperature is not None else '',
                float(dato.diagnostic_temperature) if dato.diagnostic_temperature is not None else '',
                temp_redundante_corregida if temp_redundante_corregida is not None else '',
                sistema.tag
            ])
        
        return response

class DatosTiempoRealView(APIView):
    """
    CBV para obtener los últimos datos para mostrar en los displays en tiempo real
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener coeficientes de corrección
            mt, bt, mp, bp, span_presion, zero_presion = get_coeficientes_correccion(sistema)
            
            # Obtener el último registro
            ultimo_dato = NodeRedData.objects.filter(
                systemId=sistema
            ).order_by('-created_at').first()
            
            if not ultimo_dato:
                return Response({
                    'success': False,
                    'error': 'No hay datos disponibles para este sistema'
                }, status=404)
            
            # Convertir UTC a hora de Colombia
            fecha_colombia = ultimo_dato.created_at.astimezone(COLOMBIA_TZ)
            
            # Aplicar corrección a Temperatura de Salida (redundant_temperature)
            temp_salida = ultimo_dato.redundant_temperature
            temp_salida_corr = mt * float(temp_salida) + bt if temp_salida is not None else None
            
            # Aplicar corrección a Presión (pressure_out)
            presion = ultimo_dato.pressure_out
            if presion is not None:
                # 1. Convertir valor crudo con span
                valor_convertido = convertir_presion_con_span(presion, span_presion)
                # 2. Aplicar corrección mx+b
                presion_corr = mp * valor_convertido + bp
            else:
                presion_corr = None
            
            return Response({
                'success': True,
                'datos': {
                    'flujo': {
                        'valor': cm3_s_a_gal_min(ultimo_dato.flow_rate),
                        'unidad': 'gal/min'
                    },
                    'flujoMasico': {
                        'valor': lb_s_a_kg_min(ultimo_dato.mass_rate),
                        'unidad': 'kg/min'
                    },
                    'temperaturaRedundante': {
                        'valor': celsius_a_fahrenheit(temp_salida_corr) if temp_salida_corr is not None else None,
                        'unidad': '°F'
                    },
                    'temperaturaDiagnostico': {
                        'valor': celsius_a_fahrenheit(ultimo_dato.diagnostic_temperature),
                        'unidad': '°F'
                    },
                    'temperatura': {
                        'valor': celsius_a_fahrenheit(ultimo_dato.coriolis_temperature),
                        'unidad': '°F'
                    },
                    'presion': {
                        'valor': float(presion_corr) if presion_corr is not None else 0,
                        'unidad': 'PSI'
                    },
                    'volTotal': {
                        'valor': cm3_a_gal(ultimo_dato.total_volume),
                        'unidad': 'gal'
                    },
                    'masTotal': {
                        'valor': lb_a_kg(ultimo_dato.total_mass),
                        'unidad': 'kg'
                    },
                    'densidad': {
                        'valor': float(ultimo_dato.density) if ultimo_dato.density else 0,
                        'unidad': 'g/cc'
                    },
                    'frecuencia': {
                        'valor': float(ultimo_dato.coriolis_frecuency) if ultimo_dato.coriolis_frecuency else 0,
                        'unidad': 'Hz'
                    },
                    'concSolido': {
                        'valor': float(ultimo_dato.pconc) if ultimo_dato.pconc else 0,
                        'unidad': '%'
                    },
                    'corteAgua': {
                        'valor': float(ultimo_dato.percent_cutWater64b) if ultimo_dato.percent_cutWater64b else 0,
                        'unidad': '%'
                    },
                    'signalGateway': {
                        'valor': float(ultimo_dato.signal_strength_rxCoriolis) if ultimo_dato.signal_strength_rxCoriolis else 0,
                        'unidad': 'dB'
                    },
                    'tempGateway': {
                        'valor': float(ultimo_dato.temperature_gateway) if ultimo_dato.temperature_gateway else 0,
                        'unidad': '°C'  # Esta se mantiene en °C según lo solicitado
                    }
                },
                'timestamp': fecha_colombia.isoformat(),
                'fecha_legible': fecha_colombia.strftime('%d/%m/%Y %H:%M:%S')
            })
            
        except Sistema.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Sistema no encontrado'
            }, status=404)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)

class DatosTendenciasView(APIView):
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
                systemId=sistema
            ).order_by('-created_at').first()
            
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
            fecha_fin = ultimo_dato.created_at
            fecha_inicio = fecha_fin - timedelta(minutes=30)
            
            # Consultar datos en esa ventana de tiempo
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at__range=[fecha_inicio, fecha_fin]
            ).order_by('created_at')
            
            # Preparar datos para cada variable
            flujo_masico = []
            flujo_volumetrico = []
            temperatura_coriolis = []
            temperatura_salida = []
            presion = []
            
            for dato in datos:
                # Convertir UTC a hora de Colombia
                fecha_colombia = dato.created_at.astimezone(COLOMBIA_TZ)
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
                    'ultimo_dato': ultimo_dato.created_at.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S')
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
            logger.error(f"Error en DatosTendenciasView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)


class DetectarBatchesView(APIView):
    """
    CBV para detectar batches en un rango de fechas específico
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, sistema_id):
        try:
            # Obtener parámetros
            fecha_inicio_str = request.data.get('fecha_inicio')
            fecha_fin_str = request.data.get('fecha_fin')
            
            if not fecha_inicio_str or not fecha_fin_str:
                return Response({
                    'success': False,
                    'error': 'Las fechas de inicio y fin son obligatorias'
                }, status=400)
            
            # Verificar que el sistema existe
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener límites de configuración
            try:
                config = ConfiguracionCoeficientes.objects.get(systemId=sistema)
                lim_inf = config.lim_inf_caudal_masico  # En kg/min
                lim_sup = config.lim_sup_caudal_masico  # En kg/min
                vol_minimo = config.vol_masico_ini_batch  # En kg - volumen mínimo para considerar batch
            except ConfiguracionCoeficientes.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'No se encontró configuración de límites para este sistema'
                }, status=400)
            
            # Convertir fechas a datetime
            from datetime import datetime
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Convertir a timezone aware
            from django.utils import timezone as django_timezone
            fecha_inicio = django_timezone.make_aware(fecha_inicio)
            fecha_fin = django_timezone.make_aware(fecha_fin)
            
            # Obtener datos del rango de fechas, ordenados por fecha
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at__gte=fecha_inicio,
                created_at__lte=fecha_fin
            ).order_by('created_at')
            
            if not datos.exists():
                return Response({
                    'success': False,
                    'error': 'No se encontraron datos en el rango de fechas especificado'
                }, status=404)
            
            # Ejecutar algoritmo de detección de batches
            batches_detectados = self._detectar_batches(datos, lim_inf, lim_sup, vol_minimo, sistema)
            
            # Guardar batches en la base de datos
            batches_guardados = []
            for batch_data in batches_detectados:
                batch = BatchDetectado.objects.create(
                    systemId=sistema,
                    fecha_inicio=batch_data['fecha_inicio'],
                    fecha_fin=batch_data['fecha_fin'],
                    vol_total=batch_data['vol_total'],
                    temperatura_coriolis_prom=batch_data['temperatura_coriolis_prom'],
                    densidad_prom=batch_data['densidad_prom'],
                    duracion_minutos=batch_data['duracion_minutos'],
                    total_registros=batch_data['total_registros']
                )
                batches_guardados.append({
                    'id': batch.id,
                    'fecha_inicio': batch.fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin': batch.fecha_fin.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'vol_total': round(batch.vol_total, 2),
                    'temperatura_coriolis_prom': round(batch.temperatura_coriolis_prom, 2),
                    'densidad_prom': round(batch.densidad_prom, 4),
                    'duracion_minutos': round(batch.duracion_minutos, 2),
                    'total_registros': batch.total_registros
                })
            
            return Response({
                'success': True,
                'batches_detectados': len(batches_guardados),
                'batches': batches_guardados,
                'configuracion_usada': {
                    'lim_inf_caudal_masico': lim_inf,
                    'lim_sup_caudal_masico': lim_sup,
                    'vol_minimo_batch': vol_minimo
                },
                'rango_analizado': {
                    'fecha_inicio': fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin': fecha_fin.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'total_registros': datos.count()
                }
            })
            
        except Sistema.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Sistema no encontrado'
            }, status=404)
        except ValueError as e:
            return Response({
                'success': False,
                'error': f'Error en formato de fecha: {str(e)}'
            }, status=400)
        except Exception as e:
            logger.error(f"Error en DetectarBatchesView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
    
    def _detectar_batches(self, datos, lim_inf, lim_sup, vol_minimo, sistema):
        """
        Algoritmo para detectar batches basado en los criterios especificados
        
        Args:
            datos: QuerySet de NodeRedData ordenado por created_at
            lim_inf: Límite inferior de caudal másico (kg/min)
            lim_sup: Límite superior de caudal másico (kg/min)
            vol_minimo: Volumen mínimo para considerar un batch válido (kg)
            
        Nota: Los datos de mass_rate en la DB están en lb/sec y se convierten 
              automáticamente a kg/min para comparar con los límites.
        """
        batches = []
        en_batch = False
        inicio_batch = None
        datos_batch = []
        masa_inicial_batch = None
        
        logger.info(f"Iniciando detección de batches. Límites: inf={lim_inf}, sup={lim_sup}, vol_min={vol_minimo}")
        
        for i, dato in enumerate(datos):
            mass_rate_raw = dato.mass_rate  # En lb/sec
            total_mass = dato.total_mass
            
            # Verificar que tenemos los datos necesarios
            if mass_rate_raw is None or total_mass is None:
                continue
            
            # Convertir mass_rate de lb/sec a kg/min para comparar con los límites
            mass_rate_kg_min = lb_s_a_kg_min(mass_rate_raw)
            
            # Si el mass_rate está dentro de los límites válidos (ambos en kg/min)
            if lim_inf <= mass_rate_kg_min <= lim_sup:
                if not en_batch:
                    # Iniciar nuevo batch
                    inicio_batch = dato.created_at
                    masa_inicial_batch = total_mass  # En lb (se convertirá en los cálculos)
                    datos_batch = []
                    en_batch = True
                    logger.debug(f"Iniciando batch en {inicio_batch}, masa inicial: {masa_inicial_batch} lb")
                
                datos_batch.append(dato)
                
                # Calcular masa acumulada desde el inicio del batch (convertir de lb a kg)
                masa_acumulada_lb = total_mass - masa_inicial_batch if masa_inicial_batch is not None else 0
                masa_acumulada_kg = lb_a_kg(masa_acumulada_lb)
                
                # Si la masa acumulada supera el volumen mínimo (ambos en kg), es un batch válido
                if masa_acumulada_kg >= vol_minimo:
                    logger.debug(f"Batch válido detectado: masa acumulada {masa_acumulada_kg:.2f} kg >= {vol_minimo} kg")
                    continue
                    
            else:
                # El mass_rate está fuera de los límites
                if en_batch and datos_batch:
                    # Finalizar batch si tenemos datos suficientes
                    masa_final = datos_batch[-1].total_mass  # En lb
                    masa_acumulada_lb = masa_final - masa_inicial_batch if masa_inicial_batch is not None else 0
                    masa_acumulada_kg = lb_a_kg(masa_acumulada_lb)  # Convertir a kg
                    
                    # Solo guardar si supera el volumen mínimo (ambos en kg)
                    if masa_acumulada_kg >= vol_minimo:
                        # Calcular estadísticas del batch
                        temperaturas = [d.coriolis_temperature for d in datos_batch if d.coriolis_temperature is not None]
                        densidades = [d.density for d in datos_batch if d.density is not None]
                        
                        if temperaturas and densidades:
                            temp_promedio = sum(temperaturas) / len(temperaturas)
                            densidad_promedio = sum(densidades) / len(densidades)
                            
                            fin_batch = datos_batch[-1].created_at
                            duracion = (fin_batch - inicio_batch).total_seconds() / 60  # minutos
                            
                            batch_info = {
                                'fecha_inicio': inicio_batch,
                                'fecha_fin': fin_batch,
                                'vol_total': masa_acumulada_kg,  # En kg
                                'temperatura_coriolis_prom': temp_promedio,
                                'densidad_prom': densidad_promedio,
                                'duracion_minutos': duracion,
                                'total_registros': len(datos_batch)
                            }
                            
                            batches.append(batch_info)
                            logger.info(f"Batch guardado: {inicio_batch} a {fin_batch}, vol: {masa_acumulada_kg:.2f} kg")
                
                # Resetear estado
                en_batch = False
                inicio_batch = None
                datos_batch = []
                masa_inicial_batch = None
        
        # Verificar si hay un batch en curso al final de los datos
        if en_batch and datos_batch and masa_inicial_batch is not None:
            masa_final = datos_batch[-1].total_mass
            masa_acumulada_lb = masa_final - masa_inicial_batch
            masa_acumulada_kg = lb_a_kg(masa_acumulada_lb)  # Convertir a kg
            
            if masa_acumulada_kg >= vol_minimo:  # Comparar en kg
                temperaturas = [d.coriolis_temperature for d in datos_batch if d.coriolis_temperature is not None]
                densidades = [d.density for d in datos_batch if d.density is not None]
                
                if temperaturas and densidades:
                    temp_promedio = sum(temperaturas) / len(temperaturas)
                    densidad_promedio = sum(densidades) / len(densidades)
                    
                    fin_batch = datos_batch[-1].created_at
                    duracion = (fin_batch - inicio_batch).total_seconds() / 60  # minutos
                    
                    batch_info = {
                        'fecha_inicio': inicio_batch,
                        'fecha_fin': fin_batch,
                        'vol_total': masa_acumulada_kg,  # En kg
                        'temperatura_coriolis_prom': temp_promedio,
                        'densidad_prom': densidad_promedio,
                        'duracion_minutos': duracion,
                        'total_registros': len(datos_batch)
                    }
                    
                    batches.append(batch_info)
                    logger.info(f"Batch final guardado: {inicio_batch} a {fin_batch}, vol: {masa_acumulada_kg:.2f} kg")
        
        logger.info(f"Detección completada. Total de batches detectados: {len(batches)}")
        return batches


class DetalleBatchView(APIView):
    """
    CBV para obtener el detalle de un batch específico con datos para graficar
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, batch_id):
        try:
            # Obtener el batch
            batch = get_object_or_404(BatchDetectado, id=batch_id)
            
            # Obtener todos los datos del intervalo del batch
            datos = NodeRedData.objects.filter(
                systemId=batch.systemId,
                created_at__gte=batch.fecha_inicio,
                created_at__lte=batch.fecha_fin
            ).order_by('created_at')
            
            if not datos.exists():
                return Response({
                    'success': False,
                    'error': 'No se encontraron datos para este batch'
                }, status=404)
            
            # Preparar datos para el gráfico
            datos_grafico = []
            for dato in datos:
                # Convertir UTC a hora de Colombia
                fecha_colombia = dato.created_at.astimezone(COLOMBIA_TZ)
                
                # Convertir mass_rate de lb/sec a kg/min para consistencia
                mass_rate_kg_min = lb_s_a_kg_min(dato.mass_rate) if dato.mass_rate is not None else None
                
                datos_grafico.append({
                    'timestamp': int(fecha_colombia.timestamp() * 1000),  # Para Chart.js
                    'fecha_hora': fecha_colombia.strftime('%d/%m %H:%M:%S'),
                    'mass_rate_lb_s': dato.mass_rate,  # Original en lb/s
                    'mass_rate_kg_min': mass_rate_kg_min,  # Convertido a kg/min
                    'total_mass': dato.total_mass,
                    'coriolis_temperature': dato.coriolis_temperature,
                    'density': dato.density
                })
            
            return Response({
                'success': True,
                'batch_info': {
                    'id': batch.id,
                    'sistema_tag': batch.systemId.tag,
                    'fecha_inicio': batch.fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin': batch.fecha_fin.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'vol_total': batch.vol_total,
                    'temperatura_coriolis_prom': batch.temperatura_coriolis_prom,
                    'densidad_prom': batch.densidad_prom,
                    'duracion_minutos': batch.duracion_minutos,
                    'total_registros': batch.total_registros
                },
                'datos_grafico': datos_grafico,
                'total_datos': len(datos_grafico)
            })
            
        except Exception as e:
            logger.error(f"Error en DetalleBatchView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error al obtener detalle del batch: {str(e)}'
            }, status=500)
