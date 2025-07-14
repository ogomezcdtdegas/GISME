from repoGenerico.views_base import BaseListAllView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer

# 🔹 Listado
class UbicacionListAllView(BaseListAllView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    
    def get_allowed_ordering_fields(self):
        return ['created_at', 'nombre', 'latitud', 'longitud']
