from rest_framework.views import APIView
from rest_framework.response import Response
from .....models import TipoCriticidad
from .....serializers import TipoCriticidadSerializer

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
