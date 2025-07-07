from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import ProtectedError
from _AppComplementos.models import Producto, ProductoTipoCritCrit

class DeleteProductoCommand(APIView):
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Obtener el producto
                producto = Producto.objects.get(id=obj_id)
                
                # Obtener las relaciones antes de eliminar para mostrar el resumen
                relaciones = ProductoTipoCritCrit.objects.filter(
                    producto=producto
                ).select_related('relacion_tipo_criticidad__tipo_criticidad', 'relacion_tipo_criticidad__criticidad')
                
                # Recopilar información para el resumen
                nombre_producto = producto.name
                asignaciones = [
                    f"{rel.relacion_tipo_criticidad.tipo_criticidad.name} - {rel.relacion_tipo_criticidad.criticidad.name}"
                    for rel in relaciones
                ]
                
                # Eliminar el producto (esto eliminará en cascada las relaciones ProductoTipoCritCrit)
                producto.delete()
                
                # Preparar el mensaje de resumen
                if asignaciones:
                    # Separar el formateo de la lista para evitar el error de f-string
                    asignaciones_texto = "\n  - ".join(asignaciones)
                    mensaje = (
                        f'Se ha eliminado el producto "{nombre_producto}" y todas sus relaciones:\n\n'
                        '• Se eliminaron las siguientes asignaciones de criticidad:\n'
                        f'  - {asignaciones_texto}'
                    )
                    return Response({
                        'success': True,
                        'message': mensaje,
                        'detalles': {
                            'asignaciones_eliminadas': asignaciones
                        }
                    }, status=status.HTTP_200_OK)
                
                # Si no había relaciones, mensaje simple
                return Response({
                    'success': True,
                    'message': f'Producto "{nombre_producto}" eliminado correctamente'
                }, status=status.HTTP_200_OK)
                
        except Producto.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Producto no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except ProtectedError:
            return Response({
                'success': False,
                'message': 'No se puede eliminar el producto porque tiene dependencias'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar el producto: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
