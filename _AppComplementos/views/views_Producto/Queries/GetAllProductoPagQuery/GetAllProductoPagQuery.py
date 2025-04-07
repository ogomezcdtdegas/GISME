from repoGenerico.views_base import BaseListView
from .....models import ProductoTipoCritCrit
from .....serializers import ProductoTipoCriticiddadSerializer

# 🔹 Listado paginado
class allProductosPag(BaseListView):
    model = ProductoTipoCritCrit
    serializer_class = ProductoTipoCriticiddadSerializer
    template_name = "_AppComplementos/templates_producto/index.html"

    def get(self, request):
        # Forzar 10 registros por página si no se especifica
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = '10'  # Valor por defecto
        return super().get(request)