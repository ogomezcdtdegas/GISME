
from repoGenerico.views_base import BaseListView
from .....models import Criticidad
from .....serializers import CriticidadSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response

# 🔹 API paginada (JSON)
@extend_schema_view(
    get=extend_schema(tags=['Criticidad'], description="Listado paginado de criticidades (API)")
)
class CriticidadPaginatedAPI(BaseListView):
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
    def get_queryset(self):
        return self.model.objects.all()
    model = Criticidad
    serializer_class = CriticidadSerializer

    def get_allowed_ordering_fields(self):
        return ['created_at', 'name']

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
class CriticidadPaginatedHTML(BaseListView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    template_name = "_AppComplementos/templates_criticidad/index.html"

    def get_allowed_ordering_fields(self):
        return ['created_at', 'name']

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "complementos_criticidad"
        return context