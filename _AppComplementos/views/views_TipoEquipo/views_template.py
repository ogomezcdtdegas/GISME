from ...models import TipoEquipoProducto
from ...serializers import TipoEquipoProductoSerializer
from repoGenerico.views_base import BaseListView
from django.db.models import Count

# 🔹 Vista HTML paginada
class TipoEquipoPaginatedHTML(BaseListView):
    model = TipoEquipoProducto
    serializer_class = TipoEquipoProductoSerializer
    template_name = "_AppComplementos/templates_tipoEquipo/index.html"
    active_section = "complementos_tipoequipo"

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

    def get_search_fields(self):
        return ['tipo_equipo__name']
