from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Count
from _AppComplementos.models import TipoCriticidadCriticidad, ProductoTipoCritCrit, Producto

class DeleteTipoCriticidadRelacionCommand(APIView):
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Obtener la relación específica
                relacion = TipoCriticidadCriticidad.objects.select_related(
                    'tipo_criticidad',
                    'criticidad'
                ).get(id=obj_id)
                
                # Guardar la información antes de eliminar
                tipo_criticidad = relacion.tipo_criticidad
                tipo_criticidad_id = tipo_criticidad.id
                info = {
                    'tipo_criticidad': relacion.tipo_criticidad.name,
                    'criticidad': relacion.criticidad.name
                }

                # 1. Identificar productos afectados y guardar sus nombres
                productos_afectados = ProductoTipoCritCrit.objects.filter(
                    relacion_tipo_criticidad=relacion
                ).select_related('producto')
                
                # Guardar información de productos que serán afectados
                productos_info = []
                productos_a_eliminar = set()  # Set para productos que quedarán sin relaciones

                for prod_rel in productos_afectados:
                    producto = prod_rel.producto
                    # Contar todas las relaciones de este producto
                    total_relaciones_producto = ProductoTipoCritCrit.objects.filter(
                        producto=producto
                    ).count()
                    
                    productos_info.append({
                        'nombre': producto.name,
                        'total_relaciones': total_relaciones_producto
                    })
                    
                    # Si el producto solo tiene esta relación, se marcará para eliminación
                    if total_relaciones_producto == 1:
                        productos_a_eliminar.add(producto)

                # 2. Verificar si es la última relación del tipo de criticidad
                total_relaciones = TipoCriticidadCriticidad.objects.filter(
                    tipo_criticidad=tipo_criticidad
                ).count()
                was_last_relation = total_relaciones == 1

                # 3. Construir mensaje detallado
                mensaje_productos = ""
                if productos_info:
                    mensaje_productos = "\nProductos afectados:\n"
                    for prod_info in productos_info:
                        if prod_info['nombre'] in [p.name for p in productos_a_eliminar]:
                            mensaje_productos += f"• {prod_info['nombre']} (eliminado por quedar sin relaciones)\n"
                        else:
                            mensaje_productos += f"• {prod_info['nombre']} (actualizado)\n"

                # 4. Realizar las eliminaciones
                if was_last_relation:
                    # Si es la última relación del tipo, eliminar el tipo completo
                    tipo_criticidad.delete()  # Esto eliminará en cascada todas las relaciones
                else:
                    # Solo eliminar la relación específica
                    relacion.delete()

                # 5. Eliminar productos que quedaron sin relaciones
                for producto in productos_a_eliminar:
                    producto.delete()

                return Response({
                    'success': True,
                    'was_last_relation': was_last_relation,
                    'tipo_criticidad_id': tipo_criticidad_id,
                    'productos_eliminados': [p.name for p in productos_a_eliminar],
                    'message': (
                        f'Se ha eliminado el tipo de criticidad "{info["tipo_criticidad"]}" completamente ya que esta era su última relación.\n\n'
                        if was_last_relation else
                        f'Se ha eliminado la relación del tipo de criticidad "{info["tipo_criticidad"]}".\n\n'
                    ) + (
                        'Se eliminó la siguiente relación:\n'
                        f'• Criticidad: {info["criticidad"]}\n\n'
                    ) + (
                        'Como era la última relación, el tipo de criticidad ha sido eliminado del sistema.\n\n'
                        if was_last_relation else ''
                    ) + mensaje_productos
                }, status=status.HTTP_200_OK)

        except TipoCriticidadCriticidad.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No se encontró la relación especificada.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar la relación: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
