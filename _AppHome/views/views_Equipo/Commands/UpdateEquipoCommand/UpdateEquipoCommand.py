from repoGenerico.views_base import BaseRetrieveUpdateView
from .....models import Equipo
from .....serializers import EquipoSerializer

# 🔹 Edición
class editarEquipo(BaseRetrieveUpdateView):
    model = Equipo
    serializer_class = EquipoSerializer