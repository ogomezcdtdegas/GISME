from repoGenerico.views_base import BaseReadForIdView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['Ubicación']),
    post=extend_schema(tags=['Ubicación']),
)

# 🔹 Obtener por ID
class GetUbicacionByIdView(BaseReadForIdView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    permission_classes = [IsAuthenticated]
