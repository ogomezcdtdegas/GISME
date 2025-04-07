from repoGenerico.views_base import BaseListView
from .....models import TipoCriticidadCriticidad
from .....serializers import TipoCriticidadCriticidadSerializer

# 🔹 Listado paginado
class allTipCriticidadPag(BaseListView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer
    template_name = "_AppComplementos/templates_tipoCriticidad/index.html"

    def get(self, request):
        # Forzar 10 registros por página si no se especifica
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'  # Valor por defecto
        return super().get(request)