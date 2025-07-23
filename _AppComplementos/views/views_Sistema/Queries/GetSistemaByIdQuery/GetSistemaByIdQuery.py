from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseRetrieveView

from .....models import Sistema
from .....serializers import SistemaSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['Sistema']),
    post=extend_schema(tags=['Sistema']),
)

class ObtenerSistemaQueryView(BaseRetrieveView):
    """CBV Query para obtener un sistema específico usando BaseRetrieveView"""
    model = Sistema
    serializer_class = SistemaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Optimizar consulta con select_related para ubicación"""
        return Sistema.objects.select_related('ubicacion')
