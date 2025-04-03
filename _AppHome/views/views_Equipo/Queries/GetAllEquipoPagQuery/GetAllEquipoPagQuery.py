from repoGenerico.views_base import BaseListView
from .....models import Equipo
from .....serializers import EquipoSerializer

# 🔹 Listado paginado
class allEquiposPag(BaseListView):
    model = Equipo
    serializer_class = EquipoSerializer
    template_name = "_AppHome/index.html"