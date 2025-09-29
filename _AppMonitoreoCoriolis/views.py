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
from _AppComplementos.models import Sistema

# Configurar logging
logger = logging.getLogger(__name__)

# Configurar zona horaria de Colombia
COLOMBIA_TZ = pytz.timezone('America/Bogota')

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
                
                # Flujo volumétrico
                if dato.flow_rate is not None:
                    flujo_volumetrico.append({
                        'fecha': fecha_str,
                        'valor': float(dato.flow_rate),
                        'timestamp': timestamp
                    })
                
                # Flujo másico
                if dato.mass_rate is not None:
                    flujo_masico.append({
                        'fecha': fecha_str,
                        'valor': float(dato.mass_rate),
                        'timestamp': timestamp
                    })
            
            return Response({
                'success': True,
                'flujo_volumetrico': {
                    'datos': flujo_volumetrico,
                    'unidad': 'm³/h',
                    'total_registros': len(flujo_volumetrico)
                },
                'flujo_masico': {
                    'datos': flujo_masico,
                    'unidad': 'kg/h',
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
                
                # Usar pressure_out como solicitado
                if dato.pressure_out is not None:
                    datos_presion.append({
                        'fecha': fecha_str,
                        'valor': float(dato.pressure_out),
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
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="presion_{sistema.tag}_{fecha_inicio.strftime("%Y%m%d")}_{fecha_fin.strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Hora', 'Presión (PSI)', 'Sistema'])
        
        for dato in datos:
            if dato.pressure_out is not None:
                fecha_colombia = dato.created_at.astimezone(COLOMBIA_TZ)
                writer.writerow([
                    fecha_colombia.strftime('%d/%m/%Y'),
                    fecha_colombia.strftime('%H:%M:%S'),
                    float(dato.pressure_out),
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
                
                # Temperatura Coriolis
                if dato.coriolis_temperature is not None:
                    datos_coriolis.append({
                        'fecha': fecha_str,
                        'valor': float(dato.coriolis_temperature),
                        'timestamp': timestamp
                    })
                
                # Temperatura Diagnóstico
                if dato.diagnostic_temperature is not None:
                    datos_diagnostic.append({
                        'fecha': fecha_str,
                        'valor': float(dato.diagnostic_temperature),
                        'timestamp': timestamp
                    })
                
                # Temperatura Redundante
                if dato.redundant_temperature is not None:
                    datos_redundant.append({
                        'fecha': fecha_str,
                        'valor': float(dato.redundant_temperature),
                        'timestamp': timestamp
                    })
            
            return Response({
                'success': True,
                'coriolis_temperature': {
                    'datos': datos_coriolis,
                    'total_registros': len(datos_coriolis),
                    'unidad': '°C'
                },
                'diagnostic_temperature': {
                    'datos': datos_diagnostic,
                    'total_registros': len(datos_diagnostic),
                    'unidad': '°C'
                },
                'redundant_temperature': {
                    'datos': datos_redundant,
                    'total_registros': len(datos_redundant),
                    'unidad': '°C'
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
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="temperatura_{sistema.tag}_{fecha_inicio.strftime("%Y%m%d")}_{fecha_fin.strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Hora', 'Temp. Coriolis (°C)', 'Temp. Diagnóstico (°C)', 'Temp. Redundante (°C)', 'Sistema'])
        
        for dato in datos:
            fecha_colombia = dato.created_at.astimezone(COLOMBIA_TZ)
            writer.writerow([
                fecha_colombia.strftime('%d/%m/%Y'),
                fecha_colombia.strftime('%H:%M:%S'),
                float(dato.coriolis_temperature) if dato.coriolis_temperature is not None else '',
                float(dato.diagnostic_temperature) if dato.diagnostic_temperature is not None else '',
                float(dato.redundant_temperature) if dato.redundant_temperature is not None else '',
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
            
            return Response({
                'success': True,
                'datos': {
                    'flujo': {
                        'valor': float(ultimo_dato.flow_rate) if ultimo_dato.flow_rate else 0,
                        'unidad': 'cm³/s'
                    },
                    'flujoMasico': {
                        'valor': float(ultimo_dato.mass_rate) if ultimo_dato.mass_rate else 0,
                        'unidad': 'lb/s'
                    },
                    'temperaturaRedundante': {
                        'valor': float(ultimo_dato.redundant_temperature) if ultimo_dato.redundant_temperature else 0,
                        'unidad': '°C'
                    },
                    'temperaturaDiagnostico': {
                        'valor': float(ultimo_dato.diagnostic_temperature) if ultimo_dato.diagnostic_temperature else 0,
                        'unidad': '°C'
                    },
                    'temperatura': {
                        'valor': float(ultimo_dato.coriolis_temperature) if ultimo_dato.coriolis_temperature else 0,
                        'unidad': '°C'
                    },
                    'presion': {
                        'valor': float(ultimo_dato.pressure_out) if ultimo_dato.pressure_out else 0,
                        'unidad': 'PSI'
                    },
                    'volTotal': {
                        'valor': float(ultimo_dato.total_volume) if ultimo_dato.total_volume else 0,
                        'unidad': 'cm³'
                    },
                    'masTotal': {
                        'valor': float(ultimo_dato.total_mass) if ultimo_dato.total_mass else 0,
                        'unidad': 'lb'
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
                        'unidad': '°C'
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
                
                # Flujo Másico
                if dato.mass_rate is not None:
                    flujo_masico.append({
                        'x': timestamp,
                        'y': float(dato.mass_rate),
                        'fecha': fecha_str
                    })
                
                # Flujo Volumétrico
                if dato.flow_rate is not None:
                    flujo_volumetrico.append({
                        'x': timestamp,
                        'y': float(dato.flow_rate),
                        'fecha': fecha_str
                    })
                
                # Temperatura Coriolis
                if dato.coriolis_temperature is not None:
                    temperatura_coriolis.append({
                        'x': timestamp,
                        'y': float(dato.coriolis_temperature),
                        'fecha': fecha_str
                    })
                
                # Temperatura de Salida (redundant_temperature)
                if dato.redundant_temperature is not None:
                    temperatura_salida.append({
                        'x': timestamp,
                        'y': float(dato.redundant_temperature),
                        'fecha': fecha_str
                    })
                
                # Presión
                if dato.pressure_out is not None:
                    presion.append({
                        'x': timestamp,
                        'y': float(dato.pressure_out),
                        'fecha': fecha_str
                    })
            
            return Response({
                'success': True,
                'datasets': {
                    'flujo_masico': {
                        'label': 'Flujo Másico',
                        'data': flujo_masico,
                        'unidad': 'lb/s',
                        'color': '#28a745',  # Verde
                        'total_registros': len(flujo_masico)
                    },
                    'flujo_volumetrico': {
                        'label': 'Flujo Volumétrico',
                        'data': flujo_volumetrico,
                        'unidad': 'cm³/s',
                        'color': '#007bff',  # Azul
                        'total_registros': len(flujo_volumetrico)
                    },
                    'temperatura_coriolis': {
                        'label': 'Temperatura Coriolis',
                        'data': temperatura_coriolis,
                        'unidad': '°C',
                        'color': '#f59416',  # Naranja
                        'total_registros': len(temperatura_coriolis)
                    },
                    'temperatura_salida': {
                        'label': 'Temperatura de Salida',
                        'data': temperatura_salida,
                        'unidad': '°C',
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
