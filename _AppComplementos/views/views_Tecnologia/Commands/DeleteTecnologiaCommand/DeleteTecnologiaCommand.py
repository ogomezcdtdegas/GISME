from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import ProtectedError
from _AppComplementos.models import (
    Tecnologia, TecnologiaTipoEquipo
)

class DeleteTecnologiaCommand(APIView):
    """CBV Command para eliminar tecnología con lógica de cascada específica"""
    permission_classes = [IsAuthenticated]
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Obtener la tecnología
                tecnologia = Tecnologia.objects.get(id=obj_id)
                
                # Obtener las relaciones antes de eliminar para mostrar el resumen
                relaciones_tecnologia = TecnologiaTipoEquipo.objects.filter(
                    tecnologia=tecnologia
                ).select_related(
                    'relacion_tipo_equipo__tipo_equipo',
                    'relacion_tipo_equipo__relacion_producto__producto',
                    'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
                    'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__criticidad'
                )
                
                # Información para el resumen
                nombre_tecnologia = tecnologia.name
                asignaciones_tipos_equipo = []
                
                for rel in relaciones_tecnologia:
                    tipo_equipo_rel = rel.relacion_tipo_equipo
                    producto_rel = tipo_equipo_rel.relacion_producto
                    asignacion = f"{tipo_equipo_rel.tipo_equipo.name} - {producto_rel.producto.name} ({producto_rel.relacion_tipo_criticidad.tipo_criticidad.name} - {producto_rel.relacion_tipo_criticidad.criticidad.name})"
                    asignaciones_tipos_equipo.append(asignacion)
                
                # ELIMINACIÓN EN CASCADA (Django se encarga de las relaciones)
                # Al eliminar la tecnología, Django eliminará automáticamente:
                # - TecnologiaTipoEquipo (CASCADE)
                tecnologia.delete()
                
                # Construir mensaje detallado
                mensaje_detallado = f'Se ha eliminado la tecnología "{nombre_tecnologia}" y todas sus relaciones:\n\n'
                
                if asignaciones_tipos_equipo:
                    asignaciones_texto = ", ".join(asignaciones_tipos_equipo)
                    mensaje_detallado += f'• Asignaciones eliminadas: {asignaciones_texto}'
                
                return Response({
                    'success': True,
                    'message': mensaje_detallado,
                    'detalles': {
                        'asignaciones_eliminadas': asignaciones_tipos_equipo
                    }
                }, status=status.HTTP_200_OK)
                
        except Tecnologia.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Tecnología no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except ProtectedError:
            return Response({
                'success': False,
                'message': 'No se puede eliminar la tecnología porque tiene dependencias'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar la tecnología: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteTecnologiaRelacionCommand(APIView):
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Obtener la relación específica
                relacion = TecnologiaTipoEquipo.objects.select_related(
                    'tecnologia',
                    'relacion_tipo_equipo__tipo_equipo',
                    'relacion_tipo_equipo__relacion_producto__producto',
                    'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
                    'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__criticidad'
                ).get(id=obj_id)
                
                # Guardar la información antes de eliminar
                tecnologia = relacion.tecnologia
                tecnologia_id = tecnologia.id
                tipo_equipo_rel = relacion.relacion_tipo_equipo
                producto_rel = tipo_equipo_rel.relacion_producto
                
                info = {
                    'tecnologia_name': tecnologia.name,
                    'tipo_equipo_name': tipo_equipo_rel.tipo_equipo.name,
                    'producto_name': producto_rel.producto.name,
                    'tipo_criticidad': producto_rel.relacion_tipo_criticidad.tipo_criticidad.name,
                    'criticidad': producto_rel.relacion_tipo_criticidad.criticidad.name
                }
                
                # Verificar si es la última relación de la tecnología
                total_relaciones = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()
                was_last_relation = total_relaciones == 1
                
                # Realizar las eliminaciones
                if was_last_relation:
                    # Eliminar la tecnología completa (esto eliminará la relación en cascada)
                    tecnologia.delete()
                else:
                    # Solo eliminar la relación específica
                    relacion.delete()
                
                # Construir mensaje detallado
                mensaje_detallado = ""
                if was_last_relation:
                    mensaje_detallado = f'Se ha eliminado la tecnología "{info["tecnologia_name"]}" completamente ya que esta era su última asignación.\n\n'
                else:
                    mensaje_detallado = f'Se ha eliminado la relación de la tecnología "{info["tecnologia_name"]}".\n\n'
                
                mensaje_detallado += f'• Relación eliminada: {info["tipo_equipo_name"]} - {info["producto_name"]} ({info["tipo_criticidad"]} - {info["criticidad"]})'
                
                return Response({
                    'success': True,
                    'was_last_relation': was_last_relation,
                    'tecnologia_id': tecnologia_id,
                    'message': mensaje_detallado,
                    'detalles': {
                        'relacion_eliminada': f"{info['tipo_equipo_name']} - {info['producto_name']} ({info['tipo_criticidad']} - {info['criticidad']})"
                    }
                }, status=status.HTTP_200_OK)

        except TecnologiaTipoEquipo.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No se encontró la relación especificada.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar la relación: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
