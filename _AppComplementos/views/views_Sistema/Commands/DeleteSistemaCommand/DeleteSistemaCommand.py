from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseDeleteView

from .....models import Sistema

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    delete=extend_schema(tags=['Sistema']),
)

class EliminarSistemaCommandView(BaseDeleteView):
    """CBV Command para eliminar un sistema usando BaseDeleteView"""
    model = Sistema
    permission_classes = [IsAuthenticated]
    
    def get_object_info(self, obj):
        """Información descriptiva del sistema para el mensaje de confirmación"""
        return f"{obj.tag} - {obj.sistema_id}"
