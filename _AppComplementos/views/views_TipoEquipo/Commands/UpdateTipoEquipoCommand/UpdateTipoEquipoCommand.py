from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from repoGenerico.views_base import BaseRetrieveUpdateView

from _AppComplementos.models import TipoEquipo, TipoEquipoProducto, ProductoTipoCritCrit
from _AppComplementos.serializers import TipoEquipoProductoSerializer


class EditarTipoEquipoView(BaseRetrieveUpdateView):
    """CBV Command para editar tipo de equipo usando BaseRetrieveUpdateView"""
    model = TipoEquipoProducto
    serializer_class = TipoEquipoProductoSerializer
    permission_classes = [IsAuthenticated]
    
    def put(self, request, **kwargs):
        """Override del método PUT para lógica específica de actualización"""
        try:
            # Extraer ID usando el método base
            obj_id = self._get_object_id_from_kwargs(kwargs)
            
            data = request.data
            name = data.get('name')
            producto_id = data.get('producto_id')
            tipo_criticidad_id = data.get('tipo_criticidad_id')
            criticidad_id = data.get('criticidad_id')
            
            # Validar que todos los campos estén presentes
            if not all([name, producto_id, tipo_criticidad_id, criticidad_id]):
                return Response({
                    'success': False,
                    'error': 'Todos los campos son obligatorios'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener la relación a actualizar
            tipo_equipo_producto = self.model.objects.get(id=obj_id)
            
            # Buscar la relación ProductoTipoCritCrit basándose en los IDs
            producto_relacion = ProductoTipoCritCrit.objects.filter(
                producto_id=producto_id,
                relacion_tipo_criticidad__tipo_criticidad_id=tipo_criticidad_id,
                relacion_tipo_criticidad__criticidad_id=criticidad_id
            ).first()

            if not producto_relacion:
                return Response({
                    'success': False,
                    'error': 'La combinación de producto, tipo de criticidad y criticidad no existe'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener el tipo de equipo actual
            tipo_equipo_actual = tipo_equipo_producto.tipo_equipo
            
            # Si el nombre cambió, verificar que no exista otro TipoEquipo con ese nombre
            if tipo_equipo_actual.name != name:
                if TipoEquipo.objects.filter(name=name).exists():
                    return Response({
                        'success': False,
                        'error': f'Ya existe un tipo de equipo con el nombre "{name}"'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Actualizar el nombre del tipo de equipo existente
                tipo_equipo_actual.name = name
                tipo_equipo_actual.save()
            
            # Verificar si ya existe esta combinación (excluyendo el registro actual)
            if TipoEquipoProducto.objects.filter(
                tipo_equipo=tipo_equipo_actual,
                relacion_producto=producto_relacion
            ).exclude(id=obj_id).exists():
                return Response({
                    'success': False,
                    'error': 'Esta combinación ya existe'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar la relación
            tipo_equipo_producto.tipo_equipo = tipo_equipo_actual
            tipo_equipo_producto.relacion_producto = producto_relacion
            tipo_equipo_producto.save()
            
            return Response({
                'success': True,
                'message': 'Tipo de equipo actualizado correctamente',
                'data': TipoEquipoProductoSerializer(tipo_equipo_producto).data
            }, status=status.HTTP_200_OK)
            
        except self.model.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Tipo de equipo no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
