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

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def paginate_queryset(self, queryset):
        from django.core.paginator import Paginator
        per_page = int(self.request.GET.get('per_page', 10))
        page_number = int(self.request.GET.get('page', 1))
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page_number)

    def get_paginated_response(self, data):
        page = self.paginate_queryset(self.get_queryset())
        return Response({
            "results": data,
            "has_previous": page.has_previous(),
            "has_next": page.has_next(),
            "previous_page_number": page.previous_page_number() if page.has_previous() else None,
            "next_page_number": page.next_page_number() if page.has_next() else None,
            "current_page": page.number,
            "total_pages": page.paginator.num_pages,
        })

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
