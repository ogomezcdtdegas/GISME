from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Count, Q
from _AppComplementos.models import Criticidad, TipoCriticidadCriticidad, TipoCriticidad, ProductoTipoCritCrit, Producto

class DeleteCriticidadCommand(APIView):
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # 1. Obtener la criticidad y su información
                criticidad = Criticidad.objects.get(id=obj_id)
                nombre_criticidad = criticidad.name

                # 2. Obtener todos los tipos y productos que serán afectados antes de eliminar
                tipos_afectados = list(TipoCriticidadCriticidad.objects.filter(
                    criticidad=criticidad
                ).values_list('tipo_criticidad', flat=True).distinct())

                productos_afectados = list(ProductoTipoCritCrit.objects.filter(
                    relacion_tipo_criticidad__criticidad=criticidad
                ).values_list('producto', flat=True).distinct())

                # 3. Eliminar la criticidad (esto eliminará las relaciones TipoCriticidadCriticidad en cascada)
                criticidad.delete()

                # 4. Verificar y limpiar tipos que quedaron sin relaciones
                tipos_eliminados = []
                if tipos_afectados:
                    # Buscar tipos sin relaciones después de eliminar la criticidad
                    for tipo_id in tipos_afectados:
                        # Verificar si el tipo todavía tiene relaciones
                        tiene_relaciones = TipoCriticidadCriticidad.objects.filter(
                            tipo_criticidad_id=tipo_id
                        ).exists()
                        
                        if not tiene_relaciones:
                            # El tipo no tiene relaciones, eliminarlo
                            try:
                                tipo = TipoCriticidad.objects.get(id=tipo_id)
                                tipos_eliminados.append({
                                    'nombre': tipo.name,
                                    'motivo': 'no quedaron relaciones'
                                })
                                tipo.delete()
                            except TipoCriticidad.DoesNotExist:
                                pass  # Ya fue eliminado

                # 5. Verificar y limpiar productos que quedaron sin relaciones
                productos_eliminados = []
                if productos_afectados:
                    # Buscar productos sin relaciones después de eliminar la criticidad
                    for producto_id in productos_afectados:
                        # Verificar si el producto todavía tiene relaciones
                        tiene_relaciones = ProductoTipoCritCrit.objects.filter(
                            producto_id=producto_id
                        ).exists()
                        
                        if not tiene_relaciones:
                            # El producto no tiene relaciones, eliminarlo
                            try:
                                producto = Producto.objects.get(id=producto_id)
                                productos_eliminados.append({
                                    'nombre': producto.name,
                                    'motivo': 'no quedaron relaciones'
                                })
                                producto.delete()
                            except Producto.DoesNotExist:
                                pass  # Ya fue eliminado

                # 6. Construir mensaje detallado
                mensaje = f'Se ha eliminado la criticidad "{nombre_criticidad}".'

                if tipos_eliminados:
                    mensaje += "\n\nTipos de criticidad eliminados por quedar sin relaciones:"
                    for tipo in tipos_eliminados:
                        mensaje += f"\n• {tipo['nombre']} ({tipo['motivo']})"

                if productos_eliminados:
                    mensaje += "\n\nProductos eliminados por quedar sin relaciones:"
                    for producto in productos_eliminados:
                        mensaje += f"\n• {producto['nombre']} ({producto['motivo']})"

                if not tipos_eliminados and not productos_eliminados:
                    mensaje += "\nNo se eliminaron tipos ni productos adicionales."

                return Response({
                    'success': True,
                    'message': mensaje,
                    'detalles': {
                        'tipos_eliminados': [t['nombre'] for t in tipos_eliminados],
                        'productos_eliminados': [p['nombre'] for p in productos_eliminados]
                    }
                }, status=status.HTTP_200_OK)

        except Criticidad.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No se encontró la criticidad especificada.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar la criticidad: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
