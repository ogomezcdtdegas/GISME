from repoGenerico.views_base import BaseListView
from .....models import TecnologiaTipoEquipo
from .....serializers import TecnologiaTipoEquipoSerializer

# 🔹 Listado paginado
class allTecnologiasPag(BaseListView):
    model = TecnologiaTipoEquipo
    serializer_class = TecnologiaTipoEquipoSerializer
    template_name = "_AppComplementos/templates_tecnologia/index.html"

    def get_allowed_ordering_fields(self):
        return ['created_at', 'tecnologia__name']

    def apply_search_filters(self, queryset, search_query):
        """Búsqueda personalizada en el campo tecnologia__name"""
        return queryset.filter(tecnologia__name__icontains=search_query)

    def get(self, request):
        # Forzar 10 registros por página si no se especifica
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'  # Valor por defecto
        
        # Forzar ordenamiento por tecnologia__name
        if 'ordering' not in request.GET:
            request.GET['ordering'] = 'tecnologia__name'
        
        return super().get(request)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "complementos_tecnologia"
        return context
