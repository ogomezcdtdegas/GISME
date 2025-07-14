from repoGenerico.views_base import BaseRetrieveUpdateView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer

# 🔹 Actualizar
class UpdateUbicacionView(BaseRetrieveUpdateView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
