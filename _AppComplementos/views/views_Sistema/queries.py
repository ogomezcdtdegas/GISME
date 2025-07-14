from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.db import IntegrityError

from ...models import Sistema
from ...serializers import SistemaSerializer
from repoGenerico.views_base import BaseRetrieveUpdateView


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_sistemas_query(request):
    """Query para listar sistemas con paginación y búsqueda"""
    try:
        # Parámetros de paginación
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Parámetros de búsqueda y ordenamiento
        search = request.GET.get('search', '').strip()
        ordering = request.GET.get('ordering', 'tag')
        
        # Validar campo de ordenamiento
        valid_orderings = ['tag', '-tag', 'sistema_id', '-sistema_id', 'ubicacion__nombre', '-ubicacion__nombre', 'created_at', '-created_at']
        if ordering not in valid_orderings:
            ordering = 'tag'
        
        # Construir queryset base con select_related para optimizar
        queryset = Sistema.objects.select_related('ubicacion').all()
        
        # Aplicar filtros de búsqueda
        if search:
            queryset = queryset.filter(
                Q(tag__icontains=search) |
                Q(sistema_id__icontains=search) |
                Q(ubicacion__nombre__icontains=search)
            )
        
        # Aplicar ordenamiento
        queryset = queryset.order_by(ordering)
        
        # Paginar resultados
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Serializar datos
        serializer = SistemaSerializer(page_obj.object_list, many=True)
        
        return Response({
            'results': serializer.data,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'search_query': search
        })
        
    except Exception as e:
        print(f"❌ Error en listar_sistemas_query: {str(e)}")
        return Response(
            {'error': f'Error al obtener sistemas: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_todos_sistemas_query(request):
    """Query para listar todos los sistemas sin paginación"""
    try:
        ordering = request.GET.get('ordering', 'tag')
        
        # Validar campo de ordenamiento
        valid_orderings = ['tag', '-tag', 'sistema_id', '-sistema_id', 'ubicacion__nombre', '-ubicacion__nombre']
        if ordering not in valid_orderings:
            ordering = 'tag'
        
        # Obtener todos los sistemas
        sistemas = Sistema.objects.select_related('ubicacion').order_by(ordering)
        serializer = SistemaSerializer(sistemas, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': sistemas.count()
        })
        
    except Exception as e:
        print(f"❌ Error en listar_todos_sistemas_query: {str(e)}")
        return Response(
            {'success': False, 'error': f'Error al obtener sistemas: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_sistema_query(request, sistema_id):
    """Query para obtener un sistema específico"""
    try:
        sistema = Sistema.objects.select_related('ubicacion').get(id=sistema_id)
        serializer = SistemaSerializer(sistema)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Sistema.DoesNotExist:
        return Response(
            {'success': False, 'error': 'Sistema no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"❌ Error en obtener_sistema_query: {str(e)}")
        return Response(
            {'success': False, 'error': f'Error al obtener sistema: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
