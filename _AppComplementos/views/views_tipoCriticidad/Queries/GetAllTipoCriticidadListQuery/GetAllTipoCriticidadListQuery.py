from repoGenerico.views_base import BaseListAllView
from .....models import TipoCriticidad
from .....serializers import TipoCriticidadSerializer

# 🔹 Listado
class TipoCriticidadListAllView(BaseListAllView):
    model = TipoCriticidad
    serializer_class = TipoCriticidadSerializer