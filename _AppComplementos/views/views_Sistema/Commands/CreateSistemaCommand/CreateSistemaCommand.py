from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseCreateView

from .....models import Sistema
from .....serializers import SistemaSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(tags=['Sistema']),
)

class CrearSistemaCommandView(BaseCreateView):
    """CBV Command para crear un nuevo sistema usando BaseCreateView"""
    model = Sistema
    serializer_class = SistemaSerializer
    permission_classes = [IsAuthenticated]
