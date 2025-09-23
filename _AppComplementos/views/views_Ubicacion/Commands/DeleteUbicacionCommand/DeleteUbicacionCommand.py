from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseDeleteView
from .....models import Ubicacion

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    delete=extend_schema(tags=['Ubicación']),
)

# 🔹 Eliminar
class DeleteUbicacionView(BaseDeleteView):
    """CBV Command para eliminar una ubicación usando BaseDeleteView"""
    model = Ubicacion
    permission_classes = [IsAuthenticated]
    
    def get_object_info(self, obj):
        """Información descriptiva de la ubicación para el mensaje de confirmación"""
        return f"{obj.nombre}"
