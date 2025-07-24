from ...models import TecnologiaTipoEquipo
from ...serializers import TecnologiaTipoEquipoSerializer
from repoGenerico.views_base import BaseListView
from django.db.models import Count

# 🔹 Vista HTML paginada
class TecnologiaPaginatedHTML(BaseListView):
    model = TecnologiaTipoEquipo
    serializer_class = TecnologiaTipoEquipoSerializer
    template_name = "_AppComplementos/templates_tecnologia/index.html"
    active_section = "complementos_tecnologia"

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

    def get_search_fields(self):
        return ['tecnologia__name']
