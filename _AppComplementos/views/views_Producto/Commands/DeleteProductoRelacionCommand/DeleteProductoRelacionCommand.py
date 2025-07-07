from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Count
from _AppComplementos.models import ProductoTipoCritCrit, Producto, TipoCriticidadCriticidad

class DeleteProductoRelacionCommand(APIView):
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Obtener la relación específica
                relacion = ProductoTipoCritCrit.objects.select_related(
                    'producto',
                    'relacion_tipo_criticidad__tipo_criticidad',
                    'relacion_tipo_criticidad__criticidad'
                ).get(id=obj_id)
                
                # Guardar la información antes de eliminar
                producto = relacion.producto
                producto_id = producto.id  # Save producto_id for response
                info = {
                    'producto_name': producto.name,
                    'tipo_criticidad': relacion.relacion_tipo_criticidad.tipo_criticidad.name,
                    'criticidad': relacion.relacion_tipo_criticidad.criticidad.name
                }

                # Verificar si es la última relación del producto
                total_relaciones = ProductoTipoCritCrit.objects.filter(producto=producto).count()
                was_last_relation = total_relaciones == 1
                
                # Verificar si es la última relación con este tipo de criticidad
                tipo_criticidad = relacion.relacion_tipo_criticidad.tipo_criticidad
                total_relaciones_tipo = TipoCriticidadCriticidad.objects.filter(
                    tipo_criticidad=tipo_criticidad
                ).count()

                mensaje_adicional = ""
                
                if was_last_relation:  # Si es la última relación del producto
                    # Eliminar el producto completo (esto eliminará la relación en cascada)
                    producto.delete()
                    if total_relaciones_tipo == 1:  # Si también es la última relación del tipo
                        tipo_criticidad.delete()
                        mensaje_adicional = f'\nAdemás, como era la última relación del tipo de criticidad "{info["tipo_criticidad"]}", este también ha sido eliminado del sistema.'
                else:
                    # Solo eliminar la relación específica
                    relacion.delete()

                return Response({
                    'success': True,
                    'was_last_relation': was_last_relation,
                    'producto_id': producto_id,
                    'message': (
                        f'Se ha eliminado el producto "{info["producto_name"]}" completamente ya que esta era su última asignación.\n\n'
                        if was_last_relation else
                        f'Se ha eliminado la relación del producto "{info["producto_name"]}".\n\n'
                    ) + (
                        'Se eliminó la siguiente relación:\n'
                        f'• Tipo de Criticidad: {info["tipo_criticidad"]}\n'
                        f'• Criticidad: {info["criticidad"]}'
                        f'{mensaje_adicional}'
                    )
                }, status=status.HTTP_200_OK)

        except ProductoTipoCritCrit.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No se encontró la relación especificada.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar la relación: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
