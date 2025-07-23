from repoGenerico.views_base import BaseListAllView
from rest_framework.views import APIView
from rest_framework.response import Response
from .....models import TipoCriticidadCriticidad, TipoCriticidad
from .....serializers import TipoCriticidadCriticidadSerializer, TipoCriticidadSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['TipoCriticidad']),
    post=extend_schema(tags=['TipoCriticidad']),
)

# 🔹 Listado de relaciones
class TipoCriticidadListAllView(BaseListAllView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer

    def get_queryset(self):
        return self.model.objects.all().select_related('tipo_criticidad', 'criticidad')



@extend_schema_view(
    get=extend_schema(tags=['TipoCriticidad']),
    post=extend_schema(tags=['TipoCriticidad']),
)

# 🔹 Listado de tipos únicos
class TiposCriticidadUnicosView(APIView):
    """
    Vista para obtener tipos de criticidad únicos (sin duplicados)
    """
    def get(self, request, format=None):
        tipos = TipoCriticidad.objects.all().order_by('name')
        serializer = TipoCriticidadSerializer(tipos, many=True)
        
        return Response({
            'success': True,
            'results': serializer.data,
            'count': len(serializer.data)
        })