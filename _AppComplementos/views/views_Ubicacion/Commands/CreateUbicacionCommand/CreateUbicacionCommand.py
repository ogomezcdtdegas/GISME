from repoGenerico.views_base import BaseCreateView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(tags=['Ubicación']),
)

# 🔹 Crear
class CreateUbicacionView(BaseCreateView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
