import logging
import pytz
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema
from _AppMonitoreoCoriolis.models import BatchDetectado
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ
from UTIL_LIB.conversiones import celsius_a_fahrenheit

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
            batches_queryset = BatchDetectado.objects.filter(
                systemId=sistema,
                fecha_inicio__gte=fecha_inicio,
                fecha_inicio__lte=fecha_fin
            ).order_by('-fecha_inicio')  # Ordenar de más reciente a más antiguo
            
            # Calcular el total de masa de TODOS los batches (no solo la página)
            from django.db.models import Sum
            total_masa_resultado = batches_queryset.aggregate(total_masa=Sum('mass_total'))
            total_masa_calculado = round(total_masa_resultado['total_masa'], 2) if total_masa_resultado['total_masa'] is not None else 0.0
            
            # Obtener parámetros de paginación
            page_number = request.data.get('page', 1)
            page_size = request.data.get('page_size', 10)
            
            # Crear paginador
            paginator = Paginator(batches_queryset, page_size)
            
            try:
                batches_page = paginator.page(page_number)
            except PageNotAnInteger:
                batches_page = paginator.page(1)
            except EmptyPage:
                batches_page = paginator.page(paginator.num_pages)
            
            # Serializar los datos de la página actual
            batches_data = []
            for batch in batches_page:
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
                    'time_finished_batch': round(batch.time_finished_batch, 1) if batch.time_finished_batch else '-'
                })
            
            logger.info(f"Listando página {page_number} de {paginator.num_pages} - {len(batches_data)} batches de {paginator.count} totales para sistema {sistema_id}")
            
            return Response({
                'success': True,
                'batches': batches_data,
                'pagination': {
                    'current_page': batches_page.number,
                    'total_pages': paginator.num_pages,
                    'total_batches': paginator.count,
                    'page_size': page_size,
                    'has_next': batches_page.has_next(),
                    'has_previous': batches_page.has_previous(),
                    'next_page': batches_page.next_page_number() if batches_page.has_next() else None,
                    'previous_page': batches_page.previous_page_number() if batches_page.has_previous() else None
                },
                'total_batches': paginator.count,  # Mantener compatibilidad
                'total_masa': total_masa_calculado,  # Total de masa calculado con la misma precisión que el dashboard
                'sistema': {
                    'id': str(sistema.id),
                    'tag': sistema.tag,
                    'sistema_id': sistema.sistema_id,
                    'ubicacion': sistema.ubicacion.nombre
                },
                'fecha_inicio': fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%Y-%m-%d %H:%M:%S'),
                'fecha_fin': fecha_fin.astimezone(COLOMBIA_TZ).strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            logger.error(f"Error listando batches: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)