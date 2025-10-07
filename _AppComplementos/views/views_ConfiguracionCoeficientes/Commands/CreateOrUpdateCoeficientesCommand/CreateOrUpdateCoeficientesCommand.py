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
            zero_presion = request.data.get('zero_presion', 0.0)
            span_presion = request.data.get('span_presion', 1.0)
            
            # Nuevos campos de configuración de batch
            lim_inf_caudal_masico = request.data.get('lim_inf_caudal_masico', 0.0)
            lim_sup_caudal_masico = request.data.get('lim_sup_caudal_masico', 1000000.0)
            vol_masico_ini_batch = request.data.get('vol_masico_ini_batch', 0.0)

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
                    'bp': float(bp),
                    'zero_presion': float(zero_presion),
                    'span_presion': float(span_presion),
                    'lim_inf_caudal_masico': float(lim_inf_caudal_masico),
                    'lim_sup_caudal_masico': float(lim_sup_caudal_masico),
                    'vol_masico_ini_batch': float(vol_masico_ini_batch)
                }
            )

            # Si ya existía, actualizar los valores
            if not created:
                coeficientes.mt = float(mt)
                coeficientes.bt = float(bt)
                coeficientes.mp = float(mp)
                coeficientes.bp = float(bp)
                coeficientes.zero_presion = float(zero_presion)
                coeficientes.span_presion = float(span_presion)
                coeficientes.lim_inf_caudal_masico = float(lim_inf_caudal_masico)
                coeficientes.lim_sup_caudal_masico = float(lim_sup_caudal_masico)
                coeficientes.vol_masico_ini_batch = float(vol_masico_ini_batch)
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
                    "bp": coeficientes.bp,
                    "lim_inf_caudal_masico": coeficientes.lim_inf_caudal_masico,
                    "lim_sup_caudal_masico": coeficientes.lim_sup_caudal_masico,
                    "vol_masico_ini_batch": coeficientes.vol_masico_ini_batch
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