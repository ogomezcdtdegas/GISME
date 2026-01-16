import logging
from django.shortcuts import get_object_or_404
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

class ListarTodosTicketsView(APIView):
    """
    CBV para listar todos los batches que tienen ticket asignado
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            # Validar que el sistema existe
            sistema = get_object_or_404(Sistema, id=sistema_id)
            
            # Obtener parámetros de paginación y búsqueda desde query params
            page_number = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 10)
            search_term = request.GET.get('search', '').strip()
            
            # Buscar todos los batches que tienen número de ticket asignado
            batches_queryset = BatchDetectado.objects.filter(
                systemId=sistema,
                num_ticket__isnull=False
            ).exclude(num_ticket='')  # Excluir strings vacíos
            
            # Aplicar filtro de búsqueda si existe (búsqueda de texto, no numérica)
            if search_term:
                # Búsqueda de texto que contenga el término (funciona con formato AAMMDD_#)
                batches_queryset = batches_queryset.filter(num_ticket__icontains=search_term)
            
            batches_queryset = batches_queryset.order_by('-fecha_inicio')  # Ordenar por fecha descendente
            
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
                    'fecha_fin': batch.fecha_fin.astimezone(COLOMBIA_TZ).strftime('%Y-%m-%d %H:%M:%S') if batch.fecha_fin else 'En curso',
                    'duracion_minutos': round((batch.fecha_fin - batch.fecha_inicio).total_seconds() / 60, 2) if batch.fecha_fin else 0,
                    'mas_total': round(batch.mass_total, 2) if batch.mass_total else 0,
                    'temperatura_prom': round(celsius_a_fahrenheit(batch.temperatura_coriolis_prom), 2) if batch.temperatura_coriolis_prom else 0,
                    'densidad_prom': round(batch.densidad_prom, 10) if batch.densidad_prom else 0,
                    'perfil_lim_inf': round(batch.perfil_lim_inf_caudal, 2) if batch.perfil_lim_inf_caudal else '-',
                    'perfil_lim_sup': round(batch.perfil_lim_sup_caudal, 2) if batch.perfil_lim_sup_caudal else '-',
                    'perfil_vol_min': round(batch.perfil_vol_minimo, 2) if batch.perfil_vol_minimo else '-',
                    'total_registros': batch.total_registros or 0,
                    'time_finished_batch': round(batch.time_finished_batch, 1) if batch.time_finished_batch else '-',
                    'estado': batch.estado if hasattr(batch, 'estado') else 'completado'
                })
            
            search_info = f" con búsqueda '{search_term}'" if search_term else ""
            logger.info(f"Listando todos los tickets{search_info} - Página {page_number} de {paginator.num_pages} - {len(batches_data)} tickets de {paginator.count} totales")
            
            return Response({
                'success': True,
                'batches': batches_data,
                'pagination': {
                    'current_page': batches_page.number,
                    'total_pages': paginator.num_pages,
                    'total_batches': paginator.count,
                    'page_size': int(page_size),
                    'has_next': batches_page.has_next(),
                    'has_previous': batches_page.has_previous(),
                    'next_page': batches_page.next_page_number() if batches_page.has_next() else None,
                    'previous_page': batches_page.previous_page_number() if batches_page.has_previous() else None
                },
                'total_batches': paginator.count,
                'search_term': search_term
            })
            
        except Exception as e:
            logger.error(f"Error listando todos los tickets: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
