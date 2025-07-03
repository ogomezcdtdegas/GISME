from repoGenerico.views_base import BaseListView
from .....models import TipoCriticidadCriticidad
from .....serializers import TipoCriticidadCriticidadSerializer

# 🔹 Listado paginado
class allTipCriticidadPag(BaseListView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer
    template_name = "_AppComplementos/templates_tipoCriticidad/index.html"

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tipo_criticidad__name']

    def apply_search_filters(self, queryset, search_query):
        """Búsqueda personalizada en el campo tipo_criticidad__name"""
        return queryset.filter(tipo_criticidad__name__icontains=search_query)

    def get(self, request):
        # Forzar 10 registros por página si no se especifica
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'  # Valor por defecto
        return super().get(request)