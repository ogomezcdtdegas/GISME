from repoGenerico.views_base import BaseRetrieveUpdateView
from .....models import TipoCriticidad
from .....serializers import TipoCriticidadSerializer

# 🔹 Edición
class editarTipCriticidad(BaseRetrieveUpdateView):
    model = TipoCriticidad
    serializer_class = TipoCriticidadSerializer