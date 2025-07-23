from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseListAllView

from .....models import Sistema
from .....serializers import SistemaSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['Sistema']),
    post=extend_schema(tags=['Sistema']),
)

class ListarTodosSistemasQueryView(BaseListAllView):
    """CBV Query para listar todos los sistemas sin paginación usando BaseListAllView"""
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
        return ['tag', '-tag', 'sistema_id', '-sistema_id', 'ubicacion__nombre', '-ubicacion__nombre']
