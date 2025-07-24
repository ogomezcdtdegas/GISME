
from repoGenerico.views_base import BaseListView
from .....models import Criticidad
from .....serializers import CriticidadSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response

# 🔹 API paginada (JSON)
@extend_schema_view(
    get=extend_schema(tags=['Criticidad'], description="Listado paginado de criticidades (API)")
)
class CriticidadPaginatedAPI(BaseListView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    def get_allowed_ordering_fields(self):
        return ['created_at', 'name']

# 🔹 Vista HTML paginada
class CriticidadPaginatedHTML(BaseListView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    template_name = "_AppComplementos/templates_criticidad/index.html"

    def get_allowed_ordering_fields(self):
        return ['created_at', 'name']

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "complementos_criticidad"
        return context