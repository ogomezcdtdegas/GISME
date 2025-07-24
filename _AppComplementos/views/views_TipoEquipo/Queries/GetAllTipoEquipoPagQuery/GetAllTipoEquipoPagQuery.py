from repoGenerico.views_base import BaseListView
from django.db.models import Count
from _AppComplementos.models import TipoEquipoProducto
from _AppComplementos.serializers import TipoEquipoProductoSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view


# 🔹 API paginada (JSON)
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['TipoEquipo'], description="Listado paginado de tipo de equipos (API)")
)

class TipoEquipoPaginatedAPI(BaseListView):
    model = TipoEquipoProducto
    serializer_class = TipoEquipoProductoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'tipo_equipo',
            'relacion_producto__producto',
            'relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
            'relacion_producto__relacion_tipo_criticidad__criticidad'
        ).annotate(total_relations=Count('tipo_equipo__tipoequipoproducto'))

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tipo_equipo__name']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(tipo_equipo__name__icontains=search_query)

# 🔹 Vista HTML paginada
class TipoEquipoPaginatedHTML(BaseListView):
    model = TipoEquipoProducto
    serializer_class = TipoEquipoProductoSerializer
    template_name = "_AppComplementos/templates_tipoEquipo/index.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'tipo_equipo',
            'relacion_producto__producto',
            'relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
            'relacion_producto__relacion_tipo_criticidad__criticidad'
        ).annotate(total_relations=Count('tipo_equipo__tipoequipoproducto'))

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tipo_equipo__name']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(tipo_equipo__name__icontains=search_query)

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'
        if 'ordering' not in request.GET:
            request.GET['ordering'] = 'tipo_equipo__name'
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'complementos_tipoequipo'
        return context
