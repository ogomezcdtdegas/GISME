
from repoGenerico.views_base import BaseListView
from .....models import Criticidad
from .....serializers import CriticidadSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response

# 🔹 API paginada (JSON)
@extend_schema_view(
    get=extend_schema(tags=['Criticidad'], description="Listado paginado de criticidades (API)")
)
class CriticidadPaginatedAPI(BaseListView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    def get_allowed_ordering_fields(self):
        return ['created_at', 'name']

