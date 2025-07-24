from repoGenerico.views_base import BaseListView
from ...models import Criticidad
from ...serializers import CriticidadSerializer

class CriticidadPaginatedHTML(BaseListView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    template_name = "_AppComplementos/templates_criticidad/index.html"
    active_section = "complementos_criticidad"

    def get_allowed_ordering_fields(self):
        return ['created_at', 'name']
