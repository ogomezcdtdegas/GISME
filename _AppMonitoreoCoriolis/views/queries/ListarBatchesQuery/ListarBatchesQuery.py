import logging
import pytz
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema
from _AppMonitoreoCoriolis.models import BatchDetectado
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ

# Configurar logging
logger = logging.getLogger(__name__)

class ListarBatchesQueryView(APIView):
    """
    CBV para listar batches detectados en un rango de fechas
    Esta vista NO ejecuta la lógica de detección, solo consulta los batches ya detectados
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, sistema_id):
        try:
            # Validar que el sistema existe
            sistema = get_object_or_404(Sistema, id=sistema_id)
            
            # Obtener parámetros de fecha
            fecha_inicio_str = request.data.get('fecha_inicio')
            fecha_fin_str = request.data.get('fecha_fin')
            
            if not fecha_inicio_str or not fecha_fin_str:
                return Response({
                    'success': False,
                    'error': 'Las fechas de inicio y fin son requeridas'
                }, status=400)
            
            # Parsear fechas con formato datetime (igual que las queries históricas)
            try:
                # Intentar formato con fecha y hora: "2025-10-16T00:00:00"
                fecha_inicio_naive = datetime.strptime(fecha_inicio_str, '%Y-%m-%dT%H:%M:%S')
                fecha_fin_naive = datetime.strptime(fecha_fin_str, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                try:
                    # Fallback a formato solo fecha: "2025-10-16"
                    fecha_inicio_naive = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                    fecha_fin_naive = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
                    
                    # Establecer horas para cubrir todo el rango del día
                    fecha_inicio_naive = fecha_inicio_naive.replace(hour=0, minute=0, second=0, microsecond=0)
                    fecha_fin_naive = fecha_fin_naive.replace(hour=23, minute=59, second=59, microsecond=999999)
                except ValueError:
                    return Response({
                        'success': False,
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS'
                    }, status=400)
                    
            # Asumir que las fechas del frontend están en hora de Colombia y convertir a UTC
            fecha_inicio = COLOMBIA_TZ.localize(fecha_inicio_naive).astimezone(pytz.UTC)
            fecha_fin = COLOMBIA_TZ.localize(fecha_fin_naive).astimezone(pytz.UTC)
            
            logger.info(f"Fechas convertidas a UTC - Inicio: {fecha_inicio}, Fin: {fecha_fin}")
            
            # Buscar batches que tengan fecha_inicio dentro del rango de fechas
            # Cualquier batch que inicie dentro del día seleccionado
            batches = BatchDetectado.objects.filter(
                systemId=sistema,
                fecha_inicio__gte=fecha_inicio,
                fecha_inicio__lte=fecha_fin
            ).order_by('fecha_inicio')
            
            # Serializar los datos
            batches_data = []
            for batch in batches:
                batches_data.append({
                    'id': str(batch.id),
                    'num_ticket': batch.num_ticket,
                    'fecha_inicio': batch.fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%Y-%m-%d %H:%M:%S'),
                    'fecha_fin': batch.fecha_fin.astimezone(COLOMBIA_TZ).strftime('%Y-%m-%d %H:%M:%S'),
                    'duracion_minutos': round((batch.fecha_fin - batch.fecha_inicio).total_seconds() / 60, 2),
                    'vol_total': round(batch.vol_total, 2) if batch.vol_total else 0,
                    'temperatura_prom': round(batch.temperatura_coriolis_prom, 2) if batch.temperatura_coriolis_prom else 0,
                    'densidad_prom': round(batch.densidad_prom, 2) if batch.densidad_prom else 0,
                    'perfil_lim_inf': round(batch.perfil_lim_inf_caudal, 2) if batch.perfil_lim_inf_caudal else '-',
                    'perfil_lim_sup': round(batch.perfil_lim_sup_caudal, 2) if batch.perfil_lim_sup_caudal else '-',
                    'perfil_vol_min': round(batch.perfil_vol_minimo, 2) if batch.perfil_vol_minimo else '-',
                    'total_registros': batch.total_registros or 0,
                })
            
            logger.info(f"Listando {len(batches_data)} batches para sistema {sistema_id} entre {fecha_inicio} y {fecha_fin}")
            
            return Response({
                'success': True,
                'batches': batches_data,
                'total_batches': len(batches_data),
                'sistema': {
                    'id': str(sistema.id),
                    'tag': sistema.tag,
                    'sistema_id': sistema.sistema_id,
                    'ubicacion': sistema.ubicacion.nombre
                },
                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d %H:%M:%S'),
                'fecha_fin': fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            logger.error(f"Error listando batches: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)