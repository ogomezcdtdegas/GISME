from repoGenerico.views_base import BaseListView
from ...models import TipoCriticidadCriticidad
from ...serializers import TipoCriticidadCriticidadSerializer
from django.db.models import Count

# 🔹 Paginated HTML View (for template rendering)
class TipoCriticidadPaginatedHTML(BaseListView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer
    template_name = "_AppComplementos/templates_tipoCriticidad/index.html"
    active_section = "complementos_tipocriticidad"

    def get_queryset(self):
        return TipoCriticidadCriticidad.objects.select_related(
            'tipo_criticidad',
            'criticidad'
        ).annotate(
            total_relations=Count('tipo_criticidad__tipocriticidadcriticidad')
        ).order_by('tipo_criticidad__name', 'criticidad__name')

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tipo_criticidad__name']

    def get_search_fields(self):
        return ['tipo_criticidad__name']
