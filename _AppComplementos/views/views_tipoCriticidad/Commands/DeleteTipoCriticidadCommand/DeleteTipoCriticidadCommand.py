from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Count, ProtectedError
from _AppComplementos.models import TipoCriticidad, TipoCriticidadCriticidad, ProductoTipoCritCrit, Producto

class DeleteTipoCriticidadCommand(APIView):
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Primero intentamos encontrar una relación TipoCriticidadCriticidad
                try:
                    relacion = TipoCriticidadCriticidad.objects.select_related('tipo_criticidad', 'criticidad').get(id=obj_id)
                    tipo_criticidad = relacion.tipo_criticidad
                except TipoCriticidadCriticidad.DoesNotExist:
                    # Si no encontramos la relación, intentamos encontrar directamente el TipoCriticidad
                    tipo_criticidad = TipoCriticidad.objects.get(id=obj_id)
                
                # Obtener las relaciones antes de eliminar para mostrar el resumen
                relaciones = TipoCriticidadCriticidad.objects.filter(
                    tipo_criticidad=tipo_criticidad
                ).select_related('criticidad')
                
                # 1. Obtener todos los productos afectados por este tipo
                productos_con_este_tipo = ProductoTipoCritCrit.objects.filter(
                    relacion_tipo_criticidad__tipo_criticidad=tipo_criticidad
                ).values('producto').distinct()

                # 2. Para cada producto, verificar si tendrá otras relaciones después de eliminar este tipo
                productos_info = []
                productos_a_eliminar = set()

                for prod_data in productos_con_este_tipo:
                    producto = Producto.objects.get(id=prod_data['producto'])
                    
                    # Contar todas las relaciones del producto
                    total_relaciones = ProductoTipoCritCrit.objects.filter(
                        producto=producto
                    ).count()
                    
                    # Contar relaciones con este tipo
                    relaciones_con_este_tipo = ProductoTipoCritCrit.objects.filter(
                        producto=producto,
                        relacion_tipo_criticidad__tipo_criticidad=tipo_criticidad
                    ).count()
                    
                    # Si todas las relaciones del producto son con este tipo, el producto quedará huérfano
                    if total_relaciones == relaciones_con_este_tipo:
                        productos_a_eliminar.add(producto)
                        productos_info.append({
                            'nombre': producto.name,
                            'estado': 'eliminado',
                            'motivo': 'sin relaciones'
                        })
                    else:
                        productos_info.append({
                            'nombre': producto.name,
                            'estado': 'actualizado',
                            'relaciones_restantes': total_relaciones - relaciones_con_este_tipo
                        })
                
                # Recopilar información para el resumen
                nombre_tipo = tipo_criticidad.name
                criticidades_relacionadas = [rel.criticidad.name for rel in relaciones]
                
                # 3. Eliminar el tipo de criticidad (esto eliminará en cascada las relaciones)
                tipo_criticidad.delete()

                # 4. Eliminar los productos que quedaron sin relaciones
                for producto in productos_a_eliminar:
                    producto.delete()

                # 5. Construir mensaje detallado
                mensaje_productos = ""
                if productos_info:
                    mensaje_productos = "\n\nProductos afectados:"
                    for prod in productos_info:
                        if prod['estado'] == 'eliminado':
                            # Separar la barra invertida de la f-string
                            linea_producto = f"• {prod['nombre']} (eliminado por quedar sin relaciones)"
                            mensaje_productos += f"\n{linea_producto}"
                        else:
                            # Separar la barra invertida de la f-string
                            linea_producto = f"• {prod['nombre']} (actualizado, mantiene {prod['relaciones_restantes']} relaciones)"
                            mensaje_productos += f"\n{linea_producto}"

                return Response({
                    'success': True,
                    'message': (
                        f'Se ha eliminado el tipo de criticidad "{nombre_tipo}" y todas sus relaciones:\n\n'
                        f'• Se eliminaron las relaciones con las siguientes criticidades: {", ".join(criticidades_relacionadas)}'
                        f'{mensaje_productos}'
                    ),
                    'detalles': {
                        'criticidades_relacionadas': criticidades_relacionadas,
                        'productos_eliminados': [p.name for p in productos_a_eliminar],
                        'productos_actualizados': [p['nombre'] for p in productos_info if p['estado'] == 'actualizado']
                    }
                }, status=status.HTTP_200_OK)

        except TipoCriticidad.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No se encontró el tipo de criticidad especificado.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar el tipo de criticidad: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
