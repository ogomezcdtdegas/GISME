from repoGenerico.views_base import BaseListView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['Ubicación']),
    post=extend_schema(tags=['Ubicación']),
)

# 🔹 Listado Paginado
class UbicacionListPagView(BaseListView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    template_name = "_AppComplementos/templates_ubicacion/index.html"
    
    def get_allowed_ordering_fields(self):
        return ['created_at', 'nombre', 'latitud', 'longitud']
    
    def get_search_fields(self):
        return ['nombre']
