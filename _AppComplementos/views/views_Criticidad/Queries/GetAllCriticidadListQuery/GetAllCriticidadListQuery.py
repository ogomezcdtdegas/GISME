from repoGenerico.views_base import BaseListAllView
from .....models import Criticidad
from .....serializers import CriticidadSerializer

# 🔹 Listado
class CriticidadListAllView(BaseListAllView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    
    def get_allowed_ordering_fields(self):
        return ['created_at', 'name']