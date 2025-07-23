from repoGenerico.views_base import BaseRetrieveUpdateView, BaseReadForIdView
from .....models import Tecnologia, TipoEquipoProducto, TecnologiaTipoEquipo
from .....serializers import TecnologiaTipoEquipoSerializer
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    put=extend_schema(tags=['Tecnología']),
    patch=extend_schema(tags=['Tecnología']),
)


# 🔹 Actualización completa
class EditarTecnologiaView(BaseRetrieveUpdateView, BaseReadForIdView):
    model = TecnologiaTipoEquipo
    serializer_class = TecnologiaTipoEquipoSerializer

    def get(self, request, obj_id):
        """ Vista GET para obtener los datos de una tecnología para edición """
        try:
            relacion = self.get_object_by_id(TecnologiaTipoEquipo, obj_id, "Tecnología no encontrada")
            serializer = self.serializer_class(relacion)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, obj_id):
        data = request.data
        new_name = data.get('name')
        tipo_equipo_id = data.get('tipo_equipo_id')
        producto_id = data.get('producto_id')
        tipo_criticidad_id = data.get('tipo_criticidad_id')
        criticidad_id = data.get('criticidad_id')

        if not all([new_name, tipo_equipo_id, producto_id, tipo_criticidad_id, criticidad_id]):
            return JsonResponse({
                'success': False, 
                'error': 'Todos los campos son obligatorios'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener la relación actual
            relacion_actual = self.get_object_by_id(TecnologiaTipoEquipo, obj_id, "La tecnología no existe")
            tecnologia_actual = relacion_actual.tecnologia

            # Si el nombre cambió, verificar que no exista otra tecnología con ese nombre
            if tecnologia_actual.name != new_name:
                if Tecnologia.objects.filter(name=new_name).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'Ya existe una tecnología con el nombre "{new_name}"'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Actualizar el nombre de la tecnología existente
                tecnologia_actual.name = new_name
                tecnologia_actual.save()
                tecnologia = tecnologia_actual
            else:
                tecnologia = tecnologia_actual

            # Buscar la nueva relación TipoEquipoProducto
            nueva_relacion_tipo_equipo = TipoEquipoProducto.objects.filter(
                tipo_equipo_id=tipo_equipo_id,
                relacion_producto__producto_id=producto_id,
                relacion_producto__relacion_tipo_criticidad__tipo_criticidad_id=tipo_criticidad_id,
                relacion_producto__relacion_tipo_criticidad__criticidad_id=criticidad_id
            ).first()

            if not nueva_relacion_tipo_equipo:
                return JsonResponse({
                    "success": False, 
                    "error": "No se encontró una relación válida con los IDs proporcionados"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si ya existe esta combinación (excluyendo el registro actual)
            if TecnologiaTipoEquipo.objects.filter(
                tecnologia=tecnologia,
                relacion_tipo_equipo=nueva_relacion_tipo_equipo
            ).exclude(id=obj_id).exists():
                return JsonResponse({
                    "success": False,
                    "error": "Esta combinación ya existe"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar la relación existente
            relacion_actual.tecnologia = tecnologia
            relacion_actual.relacion_tipo_equipo = nueva_relacion_tipo_equipo
            relacion_actual.save()

            return JsonResponse({
                "success": True, 
                "message": "Tecnología actualizada exitosamente",
                "data": TecnologiaTipoEquipoSerializer(relacion_actual).data
            }, status=status.HTTP_200_OK)

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
