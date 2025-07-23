from repoGenerico.views_base import BaseListAllView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['Ubicación']),
    post=extend_schema(tags=['Ubicación']),
)

# 🔹 Listado
class UbicacionListAllView(BaseListAllView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    
    def get_allowed_ordering_fields(self):
        return ['created_at', 'nombre', 'latitud', 'longitud']
