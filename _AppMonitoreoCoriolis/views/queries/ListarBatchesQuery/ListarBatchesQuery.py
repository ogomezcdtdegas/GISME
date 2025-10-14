import logging
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
            
            # Convertir fechas a objetos datetime
            try:
                fecha_inicio = datetime.fromisoformat(fecha_inicio_str.replace('Z', '+00:00'))
                fecha_fin = datetime.fromisoformat(fecha_fin_str.replace('Z', '+00:00'))
                
                # Convertir a timezone de Colombia
                fecha_inicio = fecha_inicio.astimezone(COLOMBIA_TZ)
                fecha_fin = fecha_fin.astimezone(COLOMBIA_TZ)
                
                # Ajustar las fechas para cubrir todo el día
                # Inicio del día para fecha_inicio
                fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
                # Final del día para fecha_fin
                fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59, microsecond=999999)
                
            except ValueError as e:
                return Response({
                    'success': False,
                    'error': f'Formato de fecha inválido: {str(e)}'
                }, status=400)
            
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
                    'fecha_inicio': batch.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S'),
                    'fecha_fin': batch.fecha_fin.strftime('%Y-%m-%d %H:%M:%S'),
                    'duracion_minutos': round((batch.fecha_fin - batch.fecha_inicio).total_seconds() / 60, 2),
                    'vol_total': round(batch.vol_total, 2) if batch.vol_total else 0,
                    'temperatura_prom': round(batch.temperatura_coriolis_prom, 2) if batch.temperatura_coriolis_prom else 0,
                    'densidad_prom': round(batch.densidad_prom, 2) if batch.densidad_prom else 0,
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