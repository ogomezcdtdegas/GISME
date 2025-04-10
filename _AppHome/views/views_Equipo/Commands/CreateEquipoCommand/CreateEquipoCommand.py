from repoGenerico.views_base import BaseCreateView
from .....models import Equipo
from .....serializers import EquipoSerializer

# 🔹 Creación independiente
class crearEquipo(BaseCreateView):
    model = Equipo
    serializer_class = EquipoSerializer