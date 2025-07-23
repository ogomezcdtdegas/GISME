from repoGenerico.views_base import BaseCreateView, BaseReadForIdView
from .....models import Tecnologia, TipoEquipoProducto, TecnologiaTipoEquipo
from .....serializers import TecnologiaTipoEquipoSerializer
from django.http import JsonResponse
from rest_framework import status

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(tags=['Tecnología']),
)

# 🔹 Creación completa (Tecnología + relación con TipoEquipoProducto)
class crearTecnologia(BaseCreateView, BaseReadForIdView):
    model = TecnologiaTipoEquipo
    serializer_class = TecnologiaTipoEquipoSerializer

    def post(self, request):
        data = request.data
        tecnologia_name = data.get('name')
        tipo_equipo_id = data.get('tipo_equipo_id')
        producto_id = data.get('producto_id')
        tipo_criticidad_id = data.get('tipo_criticidad_id')
        criticidad_id = data.get('criticidad_id')

        if not all([tecnologia_name, tipo_equipo_id, producto_id, tipo_criticidad_id, criticidad_id]):
            return JsonResponse({
                'success': False, 
                'error': 'Todos los campos son obligatorios: nombre, tipo_equipo_id, producto_id, tipo_criticidad_id, criticidad_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Crear o encontrar la tecnología
            tecnologia, _ = self.get_or_create_object(Tecnologia, name=tecnologia_name)
            
            # Buscar la relación TipoEquipoProducto existente con los IDs proporcionados
            relacion_tipo_equipo = TipoEquipoProducto.objects.filter(
                tipo_equipo_id=tipo_equipo_id,
                relacion_producto__producto_id=producto_id,
                relacion_producto__relacion_tipo_criticidad__tipo_criticidad_id=tipo_criticidad_id,
                relacion_producto__relacion_tipo_criticidad__criticidad_id=criticidad_id
            ).first()

            if not relacion_tipo_equipo:
                return JsonResponse({
                    "success": False, 
                    "error": "No se encontró una relación válida con los IDs proporcionados"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Crear la relación TecnologiaTipoEquipo
            relacion_final, created = self.get_or_create_object(
                TecnologiaTipoEquipo,
                tecnologia=tecnologia,
                relacion_tipo_equipo=relacion_tipo_equipo
            )

            if not created:
                return JsonResponse({
                    "success": False, 
                    "message": "Esta relación ya existe"
                }, status=status.HTTP_200_OK)

            return JsonResponse({
                "success": True, 
                "message": "Tecnología registrada exitosamente", 
                "data": TecnologiaTipoEquipoSerializer(relacion_final).data
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return JsonResponse({
                "success": False, 
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({
                "success": False, 
                "error": f"Error inesperado: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
