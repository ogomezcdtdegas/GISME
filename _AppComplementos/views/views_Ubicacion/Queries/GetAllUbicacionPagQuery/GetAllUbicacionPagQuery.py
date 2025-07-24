from repoGenerico.views_base import BaseListView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['Ubicación']),
    post=extend_schema(tags=['Ubicación']),
)


# 🔹 Listado Paginado API (JSON)

class UbicacionListPagView(BaseListView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    permission_classes = [IsAuthenticated]

    def get_allowed_ordering_fields(self):
        return ['created_at', 'nombre', 'latitud', 'longitud']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(nombre__icontains=search_query)
