from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .....models import ConfiguracionCoeficientes, Sistema

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    get=extend_schema(tags=['ConfiguracionCoeficientes']),
)

class GetCoeficientesBySistemaQueryView(APIView):
    """CBV Query para obtener los coeficientes de corrección de un sistema específico"""
    permission_classes = [IsAuthenticated]

    def get(self, request, sistema_id):
        """
        Obtener los coeficientes de corrección para un sistema específico.
        Si no existen coeficientes, devuelve valores por defecto.
        """
        try:
            # Verificar que el sistema existe
            try:
                sistema = Sistema.objects.get(id=sistema_id)
            except Sistema.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "El sistema especificado no existe"
                }, status=status.HTTP_404_NOT_FOUND)

            # Buscar coeficientes existentes
            try:
                coeficientes = ConfiguracionCoeficientes.objects.get(systemId=sistema)
                
                return Response({
                    "success": True,
                    "exists": True,
                    "data": {
                        "id": coeficientes.id,
                        "systemId": str(sistema.id),
                        "sistema_tag": sistema.tag,
                        "sistema_nombre": f"{sistema.tag} - {sistema.sistema_id}",
                        "mt": coeficientes.mt,
                        "bt": coeficientes.bt,
                        "mp": coeficientes.mp,
                        "bp": coeficientes.bp,
                        "created_at": coeficientes.created_at
                    }
                }, status=status.HTTP_200_OK)

            except ConfiguracionCoeficientes.DoesNotExist:
                # Si no existen coeficientes, devolver valores por defecto
                return Response({
                    "success": True,
                    "exists": False,
                    "message": "No existen coeficientes configurados para este sistema. Se muestran valores por defecto.",
                    "data": {
                        "systemId": str(sistema.id),
                        "sistema_tag": sistema.tag,
                        "sistema_nombre": f"{sistema.tag} - {sistema.sistema_id}",
                        "mt": 1.0,  # Valores por defecto
                        "bt": 0.0,
                        "mp": 1.0,
                        "bp": 0.0
                    }
                }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ Error inesperado en GetCoeficientesBySistemaQueryView: {str(e)}")
            return Response({
                "success": False,
                "error": "Error interno del servidor"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)