from django.utils import timezone
from datetime import timedelta, datetime
import pytz
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema
from _AppMonitoreoCoriolis.models import NodeRedData
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ, get_coeficientes_correccion, convertir_presion_con_span

# Configurar logging
logger = logging.getLogger(__name__)

class DatosHistoricosPresionQueryView(APIView):
    """
    CBV para obtener datos históricos de presión para un sistema específico
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            # Logging para debug
            logger.info(f"DatosHistoricosPresionQueryView - Sistema ID: {sistema_id}")
            logger.info(f"Query params: {dict(request.GET)}")
            
            # Verificar que el sistema existe
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener coeficientes de corrección
            mt, bt, mp, bp, span_presion, zero_presion = get_coeficientes_correccion(sistema)
            
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
            
            # Consultar datos
            logger.info(f"Consultando datos de presión para sistema: {sistema.tag}")
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at_iot__range=[fecha_inicio, fecha_fin],
                created_at_iot__isnull=False
            ).order_by('created_at_iot')
            
            logger.info(f"Datos encontrados: {datos.count()} registros")
            
            # Verificar si se solicita exportación CSV
            export_format = request.GET.get('export')
            if export_format == 'csv':
                return self._exportar_csv_presion(datos, sistema, fecha_inicio, fecha_fin)
            
            # Preparar datos de presión
            datos_presion = []
            
            for dato in datos:
                # Convertir UTC a hora de Colombia usando timestamp IoT
                fecha_colombia = dato.created_at_iot.astimezone(COLOMBIA_TZ)
                timestamp = int(fecha_colombia.timestamp() * 1000)
                fecha_str = fecha_colombia.strftime('%d/%m %H:%M')
                
                # Usar pressure_out con corrección del momento aplicada
                if dato.pressure_out is not None:
                    # 1. Convertir valor crudo con span
                    valor_convertido = dato.pressure_out
                    
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
            logger.error(f"Error en DatosHistoricosPresionQueryView: {str(e)}", exc_info=True)
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
        mt, bt, mp, bp, span_presion, zero_presion = get_coeficientes_correccion(sistema)
        
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