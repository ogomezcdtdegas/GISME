from repoGenerico.views_base import BaseListView
from _AppComplementos.models import Ubicacion
from _AppComplementos.serializers import UbicacionSerializer

class UbicacionListPagHTML(BaseListView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    template_name = "_AppComplementos/templates_ubicacion/index.html"

    def get_allowed_ordering_fields(self):
        return ['created_at', 'nombre', 'latitud', 'longitud']

    def get_search_fields(self):
        return ['nombre']

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'
        if 'ordering' not in request.GET:
            request.GET['ordering'] = 'nombre'
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "complementos_ubicacion"
        return context
