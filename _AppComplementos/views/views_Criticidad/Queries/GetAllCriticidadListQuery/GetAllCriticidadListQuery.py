from repoGenerico.views_base import BaseListAllView
from .....models import Criticidad
from .....serializers import CriticidadSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['Criticidad']),
    post=extend_schema(tags=['Criticidad']),
)
# 🔹 Listado
class CriticidadListAllView(BaseListAllView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    
    def get_allowed_ordering_fields(self):
        return ['created_at', 'name']