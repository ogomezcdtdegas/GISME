from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseRetrieveView

from .....models import ConfiguracionCoeficientes
from .....serializers import ConfiguracionCoeficientesSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['ConfiguracionCoeficientes']),
)
class ObtenerCoeficientesQueryView(BaseRetrieveView):
    """CBV Query para obtener coeficientes específicos por ID usando BaseRetrieveView"""
    model = ConfiguracionCoeficientes
    serializer_class = ConfiguracionCoeficientesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Optimizar consulta con select_related para sistema"""
        return ConfiguracionCoeficientes.objects.select_related('systemId')