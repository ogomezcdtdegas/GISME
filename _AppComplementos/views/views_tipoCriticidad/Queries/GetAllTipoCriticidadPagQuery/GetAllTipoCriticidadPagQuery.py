from repoGenerico.views_base import BaseListView
from .....models import TipoCriticidadCriticidad
from .....serializers import TipoCriticidadCriticidadSerializer
from django.db.models import Count

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['TipoCriticidad']),
    post=extend_schema(tags=['TipoCriticidad']),
)

# 🔹 Listado paginado
class allTipCriticidadPag(BaseListView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer
    template_name = "_AppComplementos/templates_tipoCriticidad/index.html"

    def get_queryset(self):
        """Optimizar consultas con select_related y anotaciones para evitar N+1"""
        return TipoCriticidadCriticidad.objects.select_related(
            'tipo_criticidad',
            'criticidad'
        ).annotate(
            total_relations=Count('tipo_criticidad__tipocriticidadcriticidad')
        ).order_by('tipo_criticidad__name', 'criticidad__name')

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
        
        # Forzar ordenamiento por tipo_criticidad__name para agrupar
        if 'ordering' not in request.GET:
            request.GET['ordering'] = 'tipo_criticidad__name'
        
        return super().get(request)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "complementos_tipocriticidad"
        return context