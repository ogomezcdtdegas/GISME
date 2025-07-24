from repoGenerico.views_base import BaseListView
from .....models import TecnologiaTipoEquipo
from .....serializers import TecnologiaTipoEquipoSerializer
from django.db.models import Count


from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response


# 🔹 API paginada (JSON)
@extend_schema_view(
    get=extend_schema(tags=['Tecnología'], description="Listado paginado de tecnologías (API)")
)

class TecnologiaPaginatedAPI(BaseListView):
    model = TecnologiaTipoEquipo
    serializer_class = TecnologiaTipoEquipoSerializer

    def get_queryset(self):
        return TecnologiaTipoEquipo.objects.select_related(
            'tecnologia',
            'relacion_tipo_equipo__tipo_equipo',
            'relacion_tipo_equipo__relacion_producto__producto',
            'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
            'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__criticidad'
        ).annotate(
            total_relations=Count('tecnologia__tecnologiatipoequipo')
        ).order_by('tecnologia__name')

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tecnologia__name']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(tecnologia__name__icontains=search_query)

# 🔹 Vista HTML paginada
class TecnologiaPaginatedHTML(BaseListView):
    model = TecnologiaTipoEquipo
    serializer_class = TecnologiaTipoEquipoSerializer
    template_name = "_AppComplementos/templates_tecnologia/index.html"

    def get_queryset(self):
        return TecnologiaTipoEquipo.objects.select_related(
            'tecnologia',
            'relacion_tipo_equipo__tipo_equipo',
            'relacion_tipo_equipo__relacion_producto__producto',
            'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
            'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__criticidad'
        ).annotate(
            total_relations=Count('tecnologia__tecnologiatipoequipo')
        ).order_by('tecnologia__name')

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tecnologia__name']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(tecnologia__name__icontains=search_query)

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'
        if 'ordering' not in request.GET:
            request.GET['ordering'] = 'tecnologia__name'
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "complementos_tecnologia"
        return context
