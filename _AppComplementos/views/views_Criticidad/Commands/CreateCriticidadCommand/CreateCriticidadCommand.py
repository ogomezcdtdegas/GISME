from repoGenerico.views_base import BaseCreateView
from .....models import Criticidad
from .....serializers import CriticidadSerializer

# 🔹 Creación independiente
class crearCriticidad(BaseCreateView):
    model = Criticidad
    serializer_class = CriticidadSerializer