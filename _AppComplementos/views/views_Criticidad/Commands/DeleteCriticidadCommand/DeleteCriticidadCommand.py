from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Count, Q
from _AppComplementos.models import (
    Criticidad, TipoCriticidadCriticidad, TipoCriticidad, 
    ProductoTipoCritCrit, Producto, TipoEquipoProducto, 
    TipoEquipo, TecnologiaTipoEquipo, Tecnologia
)

class DeleteCriticidadCommand(APIView):
    """CBV Command para eliminar criticidad con lógica de cascada específica"""
    permission_classes = [IsAuthenticated]
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # 1. Obtener la criticidad y su información
                criticidad = Criticidad.objects.get(id=obj_id)
                nombre_criticidad = criticidad.name

                # 2. Obtener todos los elementos afectados en la cadena ANTES de eliminar
                tipos_afectados = list(TipoCriticidadCriticidad.objects.filter(
                    criticidad=criticidad
                ).values_list('tipo_criticidad', flat=True).distinct())

                productos_afectados = list(ProductoTipoCritCrit.objects.filter(
                    relacion_tipo_criticidad__criticidad=criticidad
                ).values_list('producto', flat=True).distinct())

                tipos_equipo_afectados = list(TipoEquipoProducto.objects.filter(
                    relacion_producto__relacion_tipo_criticidad__criticidad=criticidad
                ).values_list('tipo_equipo', flat=True).distinct())

                tecnologias_afectadas = list(TecnologiaTipoEquipo.objects.filter(
                    relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__criticidad=criticidad
                ).values_list('tecnologia', flat=True).distinct())

                # 3. Eliminar la criticidad (esto eliminará las relaciones TipoCriticidadCriticidad en cascada)
                criticidad.delete()

                # 4. Verificar y limpiar tipos que quedaron sin relaciones
                tipos_eliminados = []
                if tipos_afectados:
                    for tipo_id in tipos_afectados:
                        tiene_relaciones = TipoCriticidadCriticidad.objects.filter(
                            tipo_criticidad_id=tipo_id
                        ).exists()
                        
                        if not tiene_relaciones:
                            try:
                                tipo = TipoCriticidad.objects.get(id=tipo_id)
                                tipos_eliminados.append({
                                    'nombre': tipo.name,
                                    'motivo': 'no quedaron relaciones'
                                })
                                tipo.delete()
                            except TipoCriticidad.DoesNotExist:
                                pass

                # 5. Verificar y limpiar productos que quedaron sin relaciones
                productos_eliminados = []
                if productos_afectados:
                    for producto_id in productos_afectados:
                        tiene_relaciones = ProductoTipoCritCrit.objects.filter(
                            producto_id=producto_id
                        ).exists()
                        
                        if not tiene_relaciones:
                            try:
                                producto = Producto.objects.get(id=producto_id)
                                productos_eliminados.append({
                                    'nombre': producto.name,
                                    'motivo': 'no quedaron relaciones'
                                })
                                producto.delete()
                            except Producto.DoesNotExist:
                                pass

                # 6. Verificar y limpiar tipos de equipo que quedaron sin relaciones
                tipos_equipo_eliminados = []
                if tipos_equipo_afectados:
                    for tipo_equipo_id in tipos_equipo_afectados:
                        tiene_relaciones = TipoEquipoProducto.objects.filter(
                            tipo_equipo_id=tipo_equipo_id
                        ).exists()
                        
                        if not tiene_relaciones:
                            try:
                                tipo_equipo = TipoEquipo.objects.get(id=tipo_equipo_id)
                                tipos_equipo_eliminados.append({
                                    'nombre': tipo_equipo.name,
                                    'motivo': 'no quedaron relaciones'
                                })
                                tipo_equipo.delete()
                            except TipoEquipo.DoesNotExist:
                                pass

                # 7. Verificar y limpiar tecnologías que quedaron sin relaciones
                tecnologias_eliminadas = []
                if tecnologias_afectadas:
                    for tecnologia_id in tecnologias_afectadas:
                        tiene_relaciones = TecnologiaTipoEquipo.objects.filter(
                            tecnologia_id=tecnologia_id
                        ).exists()
                        
                        if not tiene_relaciones:
                            try:
                                tecnologia = Tecnologia.objects.get(id=tecnologia_id)
                                tecnologias_eliminadas.append({
                                    'nombre': tecnologia.name,
                                    'motivo': 'no quedaron relaciones'
                                })
                                tecnologia.delete()
                            except Tecnologia.DoesNotExist:
                                pass

                # 8. Construir mensaje detallado
                mensaje = f'Se ha eliminado la criticidad "{nombre_criticidad}".'

                if tipos_eliminados:
                    mensaje += "\n\nTipos de criticidad eliminados por quedar sin relaciones:"
                    for tipo in tipos_eliminados:
                        mensaje += f"\n• {tipo['nombre']} ({tipo['motivo']})"

                if productos_eliminados:
                    mensaje += "\n\nProductos eliminados por quedar sin relaciones:"
                    for producto in productos_eliminados:
                        mensaje += f"\n• {producto['nombre']} ({producto['motivo']})"

                if tipos_equipo_eliminados:
                    mensaje += "\n\nTipos de equipo eliminados por quedar sin relaciones:"
                    for tipo_equipo in tipos_equipo_eliminados:
                        mensaje += f"\n• {tipo_equipo['nombre']} ({tipo_equipo['motivo']})"

                if tecnologias_eliminadas:
                    mensaje += "\n\nTecnologías eliminadas por quedar sin relaciones:"
                    for tecnologia in tecnologias_eliminadas:
                        mensaje += f"\n• {tecnologia['nombre']} ({tecnologia['motivo']})"

                if not any([tipos_eliminados, productos_eliminados, tipos_equipo_eliminados, tecnologias_eliminadas]):
                    mensaje += "\nNo se eliminaron elementos adicionales."

                return Response({
                    'success': True,
                    'message': mensaje,
                    'detalles': {
                        'tipos_eliminados': [t['nombre'] for t in tipos_eliminados],
                        'productos_eliminados': [p['nombre'] for p in productos_eliminados],
                        'tipos_equipo_eliminados': [te['nombre'] for te in tipos_equipo_eliminados],
                        'tecnologias_eliminadas': [t['nombre'] for t in tecnologias_eliminadas]
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
