from repoGenerico.views_base import BaseCreateView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer

# 🔹 Crear
class CreateUbicacionView(BaseCreateView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
