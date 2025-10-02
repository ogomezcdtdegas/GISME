from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .....models import ConfiguracionCoeficientes, Sistema

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(tags=['ConfiguracionCoeficientes']),
)

class CreateOrUpdateCoeficientesCommandView(APIView):
    """CBV Command para crear o actualizar coeficientes de corrección para un sistema"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Crear o actualizar coeficientes de corrección.
        Si el sistema ya tiene coeficientes, los actualiza. Si no, crea nuevos.
        """
        try:
            # Extraer datos del request
            system_id = request.data.get('systemId')
            mt = request.data.get('mt')
            bt = request.data.get('bt')
            mp = request.data.get('mp')
            bp = request.data.get('bp')

            # Validaciones básicas
            if not system_id:
                return Response({
                    "success": False,
                    "error": "El campo systemId es requerido"
                }, status=status.HTTP_400_BAD_REQUEST)

            if mt is None or bt is None or mp is None or bp is None:
                return Response({
                    "success": False,
                    "error": "Todos los coeficientes (mt, bt, mp, bp) son requeridos"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verificar que el sistema existe
            try:
                sistema = Sistema.objects.get(id=system_id)
            except Sistema.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "El sistema especificado no existe"
                }, status=status.HTTP_404_NOT_FOUND)

            # Crear o actualizar coeficientes usando get_or_create
            coeficientes, created = ConfiguracionCoeficientes.objects.get_or_create(
                systemId=sistema,
                defaults={
                    'mt': float(mt),
                    'bt': float(bt),
                    'mp': float(mp),
                    'bp': float(bp)
                }
            )

            # Si ya existía, actualizar los valores
            if not created:
                coeficientes.mt = float(mt)
                coeficientes.bt = float(bt)
                coeficientes.mp = float(mp)
                coeficientes.bp = float(bp)
                coeficientes.save()

            return Response({
                "success": True,
                "message": "Coeficientes creados exitosamente" if created else "Coeficientes actualizados exitosamente",
                "created": created,
                "data": {
                    "id": coeficientes.id,
                    "systemId": str(sistema.id),
                    "sistema_tag": sistema.tag,
                    "mt": coeficientes.mt,
                    "bt": coeficientes.bt,
                    "mp": coeficientes.mp,
                    "bp": coeficientes.bp
                }
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except ValueError as e:
            return Response({
                "success": False,
                "error": f"Error en los valores numéricos: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"❌ Error inesperado en CreateOrUpdateCoeficientesCommandView: {str(e)}")
            return Response({
                "success": False,
                "error": "Error interno del servidor"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)