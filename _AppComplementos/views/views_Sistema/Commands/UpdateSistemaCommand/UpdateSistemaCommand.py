from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseRetrieveUpdateView

from .....models import Sistema
from .....serializers import SistemaSerializer


class EditarSistemaCommandView(BaseRetrieveUpdateView):
    """CBV Command para editar un sistema existente usando BaseRetrieveUpdateView"""
    model = Sistema
    serializer_class = SistemaSerializer
    permission_classes = [IsAuthenticated]
