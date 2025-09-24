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
from .models import NodeRedData
from _AppComplementos.models import Sistema

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
            # Verificar que el sistema existe
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener parámetros de fecha
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            # Si no se especifican fechas, usar últimos 7 días
            if not fecha_inicio or not fecha_fin:
                fecha_fin = timezone.now()
                fecha_inicio = fecha_fin - timedelta(days=7)
            else:
                # Parsear fechas y establecer timezone de Colombia
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
                
                # Establecer horas para cubrir todo el rango del día en hora de Colombia
                fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
                fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                # Localizar a timezone de Colombia
                fecha_inicio = COLOMBIA_TZ.localize(fecha_inicio)
                fecha_fin = COLOMBIA_TZ.localize(fecha_fin)
                
                # Convertir a UTC para filtrar en la base de datos
                fecha_inicio = fecha_inicio.astimezone(pytz.UTC)
                fecha_fin = fecha_fin.astimezone(pytz.UTC)
            
            # Consultar datos
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at__range=[fecha_inicio, fecha_fin]
            ).order_by('created_at')
            
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
            return Response({
                'success': False,
                'error': 'Sistema no encontrado'
            }, status=404)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)

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
                        'unidad': 'm³/h'
                    },
                    'temperatura': {
                        'valor': float(ultimo_dato.coriolis_temperature) if ultimo_dato.coriolis_temperature else 0,
                        'unidad': '°F'
                    },
                    'presion': {
                        'valor': float(ultimo_dato.pressure_in) if ultimo_dato.pressure_in else 0,
                        'unidad': 'PSI'
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
