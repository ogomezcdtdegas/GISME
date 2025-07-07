from repoGenerico.views_base import BaseListView
from django.db.models import Count
from _AppComplementos.models import TipoEquipoProducto
from _AppComplementos.serializers import TipoEquipoProductoSerializer

# 🔹 Listado paginado
class allTipoEquiposPag(BaseListView):
    model = TipoEquipoProducto
    serializer_class = TipoEquipoProductoSerializer
    template_name = "_AppComplementos/templates_tipoEquipo/index.html"

    def get_queryset(self):
        """Obtener el queryset base y anotar el total de relaciones para cada tipo de equipo"""
        return super().get_queryset().select_related(
            'tipo_equipo',
            'relacion_producto__producto',
            'relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
            'relacion_producto__relacion_tipo_criticidad__criticidad'
        ).annotate(total_relations=Count('tipo_equipo__tipoequipoproducto'))

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tipo_equipo__name']

    def apply_search_filters(self, queryset, search_query):
        """Búsqueda personalizada en el campo tipo_equipo__name"""
        return queryset.filter(tipo_equipo__name__icontains=search_query)

    def get(self, request):
        # Forzar 10 registros por página si no se especifica
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'  # Valor por defecto
        
        # Establecer ordenamiento alfabético por defecto si no se especifica
        if 'ordering' not in request.GET:
            request.GET['ordering'] = 'tipo_equipo__name'  # Orden alfabético por tipo de equipo
            
        return super().get(request)
