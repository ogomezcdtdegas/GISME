from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseCreateView
from .....models import Criticidad
from .....serializers import CriticidadSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(tags=['Criticidad']),
)

# 🔹 Creación independiente
class crearCriticidad(BaseCreateView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    permission_classes = [IsAuthenticated]  # Protege la vista, solo usuarios autenticados pueden crear