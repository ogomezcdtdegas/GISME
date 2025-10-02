from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta, datetime
import pytz
import logging
from .models import NodeRedData
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes
from UTIL_LIB.conversiones import (
    celsius_a_fahrenheit, 
    lb_s_a_kg_min, 
    cm3_s_a_m3_min, 
    cm3_a_m3, 
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
        return coef.mt, coef.bt, coef.mp, coef.bp
    except ConfiguracionCoeficientes.DoesNotExist:
        # Valores por defecto: m=1, b=0 (no corrige)
        return 1.0, 0.0, 1.0, 0.0

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
                
                # Flujo volumétrico - convertir a m³/min
                if dato.flow_rate is not None:
                    valor_convertido = cm3_s_a_m3_min(float(dato.flow_rate))
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
                    'unidad': 'm³/min',
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
            mt, bt, mp, bp = get_coeficientes_correccion(sistema)
            
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
                    # Usar coeficientes del momento (mp, bp) si están disponibles, sino usar los actuales
                    mp_momento = dato.mp if dato.mp is not None else mp
                    bp_momento = dato.bp if dato.bp is not None else bp
                    presion_corregida = mp_momento * float(dato.pressure_out) + bp_momento
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
            mt, bt, mp, bp = get_coeficientes_correccion(sistema)
            
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
            mt, bt, mp, bp = get_coeficientes_correccion(sistema)
            
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
            presion_corr = mp * float(presion) + bp if presion is not None else None
            
            return Response({
                'success': True,
                'datos': {
                    'flujo': {
                        'valor': cm3_s_a_m3_min(ultimo_dato.flow_rate),
                        'unidad': 'm³/min'
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
                        'valor': cm3_a_m3(ultimo_dato.total_volume),
                        'unidad': 'm³'
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
            mt, bt, mp, bp = get_coeficientes_correccion(sistema)
            
            # Obtener datos de las últimas 4 horas
            fecha_fin = timezone.now()
            fecha_inicio = fecha_fin - timedelta(minutes=30)
            
            # Consultar datos
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
                
                # Flujo Volumétrico - convertir a m³/min
                if dato.flow_rate is not None:
                    valor_convertido = cm3_s_a_m3_min(float(dato.flow_rate))
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
                    # Usar coeficientes del momento si están disponibles, sino usar los actuales
                    mp_momento = dato.mp if dato.mp is not None else mp
                    bp_momento = dato.bp if dato.bp is not None else bp
                    presion_corregida = mp_momento * float(dato.pressure_out) + bp_momento
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
                        'unidad': 'm³/min',
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
                'periodo': '4 horas',
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
