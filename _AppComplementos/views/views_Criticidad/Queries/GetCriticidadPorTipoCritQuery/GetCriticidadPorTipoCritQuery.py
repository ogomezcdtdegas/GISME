from rest_framework.views import APIView
from rest_framework.response import Response
from .....models import TipoCriticidadCriticidad
from .....serializers import CriticidadesPorTipoSerializer
from django.shortcuts import get_object_or_404

class CriticidadesPorTipoView(APIView):
    """
    Vista para obtener criticidades filtradas por tipo de criticidad
    """
    def get(self, request, tipo_id, format=None):
        relaciones = TipoCriticidadCriticidad.objects.filter(
            tipo_criticidad_id=tipo_id
        ).select_related('criticidad')
        
        # Serializar los datos
        serializer = CriticidadesPorTipoSerializer(relaciones, many=True)
        
        # Devolver el formato esperado por el frontend
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })