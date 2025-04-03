from repoGenerico.views_base import BaseRetrieveUpdateView
from .....models import Criticidad
from .....serializers import CriticidadSerializer

# 🔹 Edición
class editarCriticidad(BaseRetrieveUpdateView):
    model = Criticidad
    serializer_class = CriticidadSerializer