from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseListAllView
from .....models import TipoCriticidadCriticidad
from .....serializers import CriticidadesPorTipoSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['Criticidad']),
    post=extend_schema(tags=['Criticidad']),
)
class CriticidadesPorTipoView(BaseListAllView):
    """CBV Query para obtener criticidades filtradas por tipo de criticidad usando BaseListAllView"""
    model = TipoCriticidadCriticidad
    serializer_class = CriticidadesPorTipoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar por tipo_id y optimizar con select_related"""
        tipo_id = self.kwargs.get('tipo_id')
        return TipoCriticidadCriticidad.objects.filter(
            tipo_criticidad_id=tipo_id
        ).select_related('criticidad')
    
    def get(self, request, tipo_id, format=None):
        """Override para capturar tipo_id del URL"""
        self.kwargs = {'tipo_id': tipo_id}
        return super().get(request)