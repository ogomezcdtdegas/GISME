from repoGenerico.views_base import BaseListView, BaseCreateView, BaseRetrieveUpdateView
from .models import Equipo
from .serializers import EquipoSerializer

# 🔹 Listado paginado
class allEquiposPag(BaseListView):
    model = Equipo
    serializer_class = EquipoSerializer
    template_name = "_AppHome/index.html"

# 🔹 Creación independiente
class crearEquipo(BaseCreateView):
    model = Equipo
    serializer_class = EquipoSerializer

# 🔹 Edición
class editarEquipo(BaseRetrieveUpdateView):
    model = Equipo
    serializer_class = EquipoSerializer
