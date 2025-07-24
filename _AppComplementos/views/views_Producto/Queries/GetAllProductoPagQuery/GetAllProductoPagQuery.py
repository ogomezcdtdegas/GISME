from repoGenerico.views_base import BaseListView
from .....models import ProductoTipoCritCrit
from .....serializers import ProductoTipoCriticiddadSerializer
from django.db.models import Count


from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response


# 🔹 API paginada (JSON)
@extend_schema_view(
    get=extend_schema(tags=['Producto'], description="Listado paginado de productos (API)")
)

class ProductoPaginatedAPI(BaseListView):
    model = ProductoTipoCritCrit
    serializer_class = ProductoTipoCriticiddadSerializer

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

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(producto__name__icontains=search_query)

# 🔹 Vista HTML paginada
class ProductoPaginatedHTML(BaseListView):
    model = ProductoTipoCritCrit
    serializer_class = ProductoTipoCriticiddadSerializer
    template_name = "_AppComplementos/templates_producto/index.html"

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

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(producto__name__icontains=search_query)

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'complementos_producto'
        return context