from repoGenerico.views_base import BaseListView
from .....models import TipoCriticidadCriticidad
from .....serializers import TipoCriticidadCriticidadSerializer
from django.db.models import Count

from drf_spectacular.utils import extend_schema, extend_schema_view

# 🔹 API paginada (JSON)
@extend_schema_view(
    get=extend_schema(tags=['TipoCriticidad'], description="Listado paginado de tecnologías (API)")
)

# 🔹 Paginated API View (for Swagger/JSON)

class TipoCriticidadPaginatedAPI(BaseListView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer

    def get_queryset(self):
        return TipoCriticidadCriticidad.objects.select_related(
            'tipo_criticidad',
            'criticidad'
        ).annotate(
            total_relations=Count('tipo_criticidad__tipocriticidadcriticidad')
        ).order_by('tipo_criticidad__name', 'criticidad__name')

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tipo_criticidad__name']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(tipo_criticidad__name__icontains=search_query)

# 🔹 Paginated HTML View (for template rendering)
class TipoCriticidadPaginatedHTML(BaseListView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer
    template_name = "_AppComplementos/templates_tipoCriticidad/index.html"

    def get_queryset(self):
        return TipoCriticidadCriticidad.objects.select_related(
            'tipo_criticidad',
            'criticidad'
        ).annotate(
            total_relations=Count('tipo_criticidad__tipocriticidadcriticidad')
        ).order_by('tipo_criticidad__name', 'criticidad__name')

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tipo_criticidad__name']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(tipo_criticidad__name__icontains=search_query)

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'
        if 'ordering' not in request.GET:
            request.GET['ordering'] = 'tipo_criticidad__name'
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "complementos_tipocriticidad"
        return context