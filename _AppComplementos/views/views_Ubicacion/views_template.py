from repoGenerico.views_base import BaseListView
from _AppComplementos.models import Ubicacion
from _AppComplementos.serializers import UbicacionSerializer

class UbicacionListPagHTML(BaseListView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    template_name = "_AppComplementos/templates_ubicacion/index.html"
    active_section = "complementos_ubicacion"

    def get_allowed_ordering_fields(self):
        return ['created_at', 'nombre', 'latitud', 'longitud']

    def get_search_fields(self):
        return ['nombre']
