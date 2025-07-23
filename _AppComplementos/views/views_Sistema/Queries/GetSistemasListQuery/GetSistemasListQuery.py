from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseListQueryView

from .....models import Sistema
from .....serializers import SistemaSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['Sistema']),
    post=extend_schema(tags=['Sistema']),
)

class ListarSistemasQueryView(BaseListQueryView):
    """CBV Query para listar sistemas con paginación y búsqueda usando BaseListQueryView"""
    model = Sistema
    serializer_class = SistemaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Optimizar consulta con select_related para ubicación"""
        return Sistema.objects.select_related('ubicacion')
    
    def get_default_ordering(self):
        """Ordenamiento por defecto"""
        return 'tag'
    
    def get_allowed_ordering_fields(self):
        """Campos permitidos para ordenamiento"""
        return ['tag', '-tag', 'sistema_id', '-sistema_id', 'ubicacion__nombre', '-ubicacion__nombre', 'created_at', '-created_at']
    
    def apply_search_filters(self, queryset, search_query):
        """Filtros de búsqueda específicos para Sistema"""
        return queryset.filter(
            Q(tag__icontains=search_query) |
            Q(sistema_id__icontains=search_query) |
            Q(ubicacion__nombre__icontains=search_query)
        )
