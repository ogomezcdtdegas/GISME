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
from UTIL_LIB.conversiones import celsius_a_fahrenheit

# Configurar logging
logger = logging.getLogger(__name__)

class ListarTicketsQueryView(APIView):
    """
    CBV para listar SOLO batches que tienen número de ticket asignado
    Esta vista consulta batches ya detectados que tienen num_ticket
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            # Validar que el sistema existe
            sistema = get_object_or_404(Sistema, id=sistema_id)
            
            # Buscar batches que tengan número de ticket asignado
            # Filtrar solo batches con num_ticket no nulo
            # Ordenar por número de ticket para facilitar la búsqueda
            batches = BatchDetectado.objects.filter(
                systemId=sistema,
                num_ticket__isnull=False
            ).order_by('num_ticket', '-fecha_inicio')  # Por ticket primero, luego más recientes
            
            # Serializar los datos
            batches_data = []
            for batch in batches:
                batches_data.append({
                    'id': str(batch.id),
                    'num_ticket': batch.num_ticket,
                    'fecha_inicio': batch.fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%Y-%m-%d %H:%M:%S'),
                    'fecha_fin': batch.fecha_fin.astimezone(COLOMBIA_TZ).strftime('%Y-%m-%d %H:%M:%S'),
                    'duracion_minutos': round((batch.fecha_fin - batch.fecha_inicio).total_seconds() / 60, 2),
                    'mas_total': round(batch.mass_total, 2) if batch.mass_total else 0,
                    'temperatura_prom': round(celsius_a_fahrenheit(batch.temperatura_coriolis_prom), 2) if batch.temperatura_coriolis_prom else 0,
                    'densidad_prom': round(batch.densidad_prom, 10) if batch.densidad_prom else 0,
                    'perfil_lim_inf': round(batch.perfil_lim_inf_caudal, 2) if batch.perfil_lim_inf_caudal else '-',
                    'perfil_lim_sup': round(batch.perfil_lim_sup_caudal, 2) if batch.perfil_lim_sup_caudal else '-',
                    'perfil_vol_min': round(batch.perfil_vol_minimo, 2) if batch.perfil_vol_minimo else '-',
                    'total_registros': batch.total_registros or 0,
                })
            
            logger.info(f"Listando {len(batches_data)} batches con ticket para sistema {sistema_id}")
            
            return Response({
                'success': True,
                'batches': batches_data,
                'total_batches': len(batches_data),
                'sistema': {
                    'id': str(sistema.id),
                    'tag': sistema.tag,
                    'sistema_id': sistema.sistema_id,
                    'ubicacion': sistema.ubicacion.nombre if sistema.ubicacion else 'Sin ubicación'
                }
            })
            
        except Exception as e:
            logger.error(f"Error listando tickets: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)