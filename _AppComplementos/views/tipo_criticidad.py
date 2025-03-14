from repoGenerico.views_base import BaseListView, BaseListAllView, BaseCreateView, BaseRetrieveUpdateView
from ..models import TipoCriticidad, Criticidad
from ..serializers import TipoCriticidadSerializer, CriticidadSerializer

# 🔹 Listado
class CriticidadListAllView(BaseListAllView):
    model = Criticidad
    serializer_class = CriticidadSerializer

# 🔹 Listado paginado
class allTipCriticidadPag(BaseListView):
    model = TipoCriticidad
    serializer_class = TipoCriticidadSerializer
    template_name = "_AppComplementos/templates_tipoCriticidad/index.html"

# 🔹 Creación independiente
class crearTipCriticidad(BaseCreateView):
    model = TipoCriticidad
    serializer_class = TipoCriticidadSerializer

# 🔹 Edición
class editarTipCriticidad(BaseRetrieveUpdateView):
    model = TipoCriticidad
    serializer_class = TipoCriticidadSerializer