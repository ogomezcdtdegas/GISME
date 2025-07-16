from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseRetrieveView

from .....models import Sistema
from .....serializers import SistemaSerializer


class ObtenerSistemaQueryView(BaseRetrieveView):
    """CBV Query para obtener un sistema específico usando BaseRetrieveView"""
    model = Sistema
    serializer_class = SistemaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Optimizar consulta con select_related para ubicación"""
        return Sistema.objects.select_related('ubicacion')
