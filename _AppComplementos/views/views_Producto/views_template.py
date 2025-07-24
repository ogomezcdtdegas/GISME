from ...models import ProductoTipoCritCrit
from ...serializers import ProductoTipoCriticiddadSerializer
from repoGenerico.views_base import BaseListView
from django.db.models import Count

# 🔹 Vista HTML paginada
class ProductoPaginatedHTML(BaseListView):
    model = ProductoTipoCritCrit
    serializer_class = ProductoTipoCriticiddadSerializer
    template_name = "_AppComplementos/templates_producto/index.html"
    active_section = "complementos_producto"

    def get_queryset(self):
        return ProductoTipoCritCrit.objects.select_related(
            'producto',
            'relacion_tipo_criticidad',
            'relacion_tipo_criticidad__tipo_criticidad',
            'relacion_tipo_criticidad__criticidad'
        ).annotate(
            total_relations=Count('producto__productotipocritcrit')
        ).order_by('producto__name', 'relacion_tipo_criticidad__tipo_criticidad__name')

    def get_allowed_ordering_fields(self):
        return ['created_at', 'producto__name']

    def get_search_fields(self):
        return ['producto__name']
