from repoGenerico.views_base import BaseRetrieveUpdateView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    put=extend_schema(tags=['Ubicación']),
    patch=extend_schema(tags=['Ubicación']),
)


# 🔹 Actualizar
class UpdateUbicacionView(BaseRetrieveUpdateView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
