from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .....models import Ubicacion

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    delete=extend_schema(tags=['Ubicación']),
)

# 🔹 Eliminar
class DeleteUbicacionView(APIView):
    def delete(self, request, ubicacion_id):
        try:
            ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id)
            ubicacion.delete()
            return Response({
                "success": True, 
                "message": "Ubicación eliminada exitosamente"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, 
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
