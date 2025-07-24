from repoGenerico.views_base import BaseListQueryView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer


from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

@extend_schema_view(
    get=extend_schema(tags=['Ubicación']),
    post=extend_schema(tags=['Ubicación']),
)

class UbicacionListAllView(BaseListQueryView):
    """CBV Query para listar ubicaciones con paginación y búsqueda usando BaseListQueryView"""
    model = Ubicacion
    serializer_class = UbicacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ubicacion.objects.all()

    def get_default_ordering(self):
        return 'created_at'

    def get_allowed_ordering_fields(self):
        return ['created_at', '-created_at', 'nombre', '-nombre', 'latitud', '-latitud', 'longitud', '-longitud']

    def apply_search_filters(self, queryset, search_query):
        return queryset.filter(
            Q(nombre__icontains=search_query) |
            Q(latitud__icontains=search_query) |
            Q(longitud__icontains=search_query)
        )
