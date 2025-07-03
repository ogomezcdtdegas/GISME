from repoGenerico.views_base import BaseListView
from .....models import Criticidad
from .....serializers import CriticidadSerializer

# 🔹 Listado paginado
class allCriticidadPag(BaseListView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    template_name = "_AppComplementos/templates_criticidad/index.html"

    def get_allowed_ordering_fields(self):
        return ['created_at', 'name']

    def get(self, request):
        # Forzar 10 registros por página si no se especifica
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'  # Valor por defecto
        return super().get(request)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "complementos_criticidad"  # Usa el nombre que corresponda a tu menú
        return context