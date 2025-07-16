from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseCreateView

from .....models import Sistema
from .....serializers import SistemaSerializer


class CrearSistemaCommandView(BaseCreateView):
    """CBV Command para crear un nuevo sistema usando BaseCreateView"""
    model = Sistema
    serializer_class = SistemaSerializer
    permission_classes = [IsAuthenticated]
