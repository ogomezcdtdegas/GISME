from repoGenerico.views_base import BaseRetrieveUpdateView
from .....models import Criticidad
from .....serializers import CriticidadSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    put=extend_schema(tags=['Criticidad']),
    patch=extend_schema(tags=['Criticidad']),
)

# 🔹 Edición
class editarCriticidad(BaseRetrieveUpdateView):
    model = Criticidad
    serializer_class = CriticidadSerializer