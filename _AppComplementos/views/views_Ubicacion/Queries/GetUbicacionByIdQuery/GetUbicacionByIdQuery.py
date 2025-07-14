from repoGenerico.views_base import BaseReadForIdView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer

# 🔹 Obtener por ID
class GetUbicacionByIdView(BaseReadForIdView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
