from repoGenerico.views_base import BaseListView
from .....models import TipoCriticidadCriticidad
from .....serializers import TipoCriticidadCriticidadSerializer
from django.db.models import Count

from drf_spectacular.utils import extend_schema, extend_schema_view

# 🔹 API paginada (JSON)
@extend_schema_view(
    get=extend_schema(tags=['TipoCriticidad'], description="Listado paginado de tecnologías (API)")
)

# 🔹 Paginated API View (for Swagger/JSON)
class TipoCriticidadPaginatedAPI(BaseListView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer

    def get_queryset(self):
        return TipoCriticidadCriticidad.objects.select_related(
            'tipo_criticidad',
            'criticidad'
        ).annotate(
            total_relations=Count('tipo_criticidad__tipocriticidadcriticidad')
        ).order_by('tipo_criticidad__name', 'criticidad__name')

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tipo_criticidad__name']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(tipo_criticidad__name__icontains=search_query)

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
        from rest_framework.response import Response
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
        if 'ordering' not in request.GET:
            request.GET['ordering'] = 'tipo_criticidad__name'
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        from rest_framework.response import Response
        return Response(serializer.data)

# 🔹 Paginated HTML View (for template rendering)
class TipoCriticidadPaginatedHTML(BaseListView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer
    template_name = "_AppComplementos/templates_tipoCriticidad/index.html"

    def get_queryset(self):
        return TipoCriticidadCriticidad.objects.select_related(
            'tipo_criticidad',
            'criticidad'
        ).annotate(
            total_relations=Count('tipo_criticidad__tipocriticidadcriticidad')
        ).order_by('tipo_criticidad__name', 'criticidad__name')

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tipo_criticidad__name']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(tipo_criticidad__name__icontains=search_query)

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'
        if 'ordering' not in request.GET:
            request.GET['ordering'] = 'tipo_criticidad__name'
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "complementos_tipocriticidad"
        return context