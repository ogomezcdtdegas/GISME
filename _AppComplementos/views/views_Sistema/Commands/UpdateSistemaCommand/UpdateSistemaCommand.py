from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseRetrieveUpdateView

from .....models import Sistema
from .....serializers import SistemaSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    put=extend_schema(tags=['Sistema']),
    patch=extend_schema(tags=['Sistema']),
)

class EditarSistemaCommandView(BaseRetrieveUpdateView):
    """CBV Command para editar un sistema existente usando BaseRetrieveUpdateView"""
    model = Sistema
    serializer_class = SistemaSerializer
    permission_classes = [IsAuthenticated]
