from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import ProtectedError
from _AppComplementos.models import (
    TipoEquipo, TipoEquipoProducto,
    Tecnologia, TecnologiaTipoEquipo
)


class DeleteTipoEquipoCommand(APIView):
    """CBV Command para eliminar tipo de equipo con lógica de cascada específica"""
    permission_classes = [IsAuthenticated]
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Obtener el tipo de equipo
                tipo_equipo = TipoEquipo.objects.get(id=obj_id)
                
                # Obtener las relaciones antes de eliminar para mostrar el resumen
                relaciones_tipo_equipo = TipoEquipoProducto.objects.filter(
                    tipo_equipo=tipo_equipo
                ).select_related('relacion_producto__producto', 'relacion_producto__relacion_tipo_criticidad__tipo_criticidad', 'relacion_producto__relacion_tipo_criticidad__criticidad')
                
                # Información para el resumen
                nombre_tipo_equipo = tipo_equipo.name
                asignaciones_productos = [
                    f"{rel.relacion_producto.producto.name} ({rel.relacion_producto.relacion_tipo_criticidad.tipo_criticidad.name} - {rel.relacion_producto.relacion_tipo_criticidad.criticidad.name})"
                    for rel in relaciones_tipo_equipo
                ]
                
                # Rastrear elementos que serán eliminados
                tecnologias_eliminadas = []
                tecnologias_actualizadas = []
                
                # 1. NIVEL TECNOLOGÍAS: Verificar tecnologías afectadas
                tecnologias_con_este_tipo = TecnologiaTipoEquipo.objects.filter(
                    relacion_tipo_equipo__in=relaciones_tipo_equipo
                ).select_related('tecnologia', 'relacion_tipo_equipo')
                
                tecnologias_a_eliminar = set()
                for tech_rel in tecnologias_con_este_tipo:
                    tecnologia = tech_rel.tecnologia
                    # Contar todas las relaciones de la tecnología
                    total_relaciones = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()
                    # Contar relaciones con este tipo de equipo
                    relaciones_con_este_tipo = TecnologiaTipoEquipo.objects.filter(
                        tecnologia=tecnologia,
                        relacion_tipo_equipo__tipo_equipo=tipo_equipo
                    ).count()
                    
                    if total_relaciones == relaciones_con_este_tipo:
                        tecnologias_a_eliminar.add(tecnologia)
                        tecnologias_eliminadas.append(tecnologia.name)
                    else:
                        tecnologias_actualizadas.append({
                            'nombre': tecnologia.name,
                            'relaciones_restantes': total_relaciones - relaciones_con_este_tipo
                        })
                
                # 2. ELIMINACIÓN EN CASCADA (Django se encarga de las relaciones)
                # Al eliminar el tipo de equipo, Django eliminará automáticamente:
                # - TipoEquipoProducto (CASCADE)
                # - TecnologiaTipoEquipo (CASCADE desde TipoEquipoProducto)
                tipo_equipo.delete()
                
                # 3. Eliminar elementos huérfanos
                for tecnologia in tecnologias_a_eliminar:
                    tecnologia.delete()
                
                # 4. Construir mensaje detallado
                mensaje_detallado = f'Se ha eliminado el tipo de equipo "{nombre_tipo_equipo}" y todas sus relaciones:\n\n'
                
                if asignaciones_productos:
                    asignaciones_texto = ", ".join(asignaciones_productos)
                    mensaje_detallado += f'• Asignaciones de productos eliminadas: {asignaciones_texto}\n'
                    
                if tecnologias_eliminadas:
                    mensaje_detallado += f'• Tecnologías eliminadas: {", ".join(tecnologias_eliminadas)}\n'
                if tecnologias_actualizadas:
                    tech_act = [f"{t['nombre']} ({t['relaciones_restantes']} relaciones)" for t in tecnologias_actualizadas]
                    mensaje_detallado += f'• Tecnologías actualizadas: {", ".join(tech_act)}'
                
                return Response({
                    'success': True,
                    'message': mensaje_detallado,
                    'detalles': {
                        'asignaciones_eliminadas': asignaciones_productos,
                        'tecnologias_eliminadas': tecnologias_eliminadas,
                        'tecnologias_actualizadas': [t['nombre'] for t in tecnologias_actualizadas]
                    }
                }, status=status.HTTP_200_OK)
                
        except TipoEquipo.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Tipo de equipo no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except ProtectedError:
            return Response({
                'success': False,
                'message': 'No se puede eliminar el tipo de equipo porque tiene dependencias'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar el tipo de equipo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteTipoEquipoRelacionCommand(APIView):
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Obtener la relación específica
                relacion = TipoEquipoProducto.objects.select_related(
                    'tipo_equipo',
                    'relacion_producto__producto',
                    'relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
                    'relacion_producto__relacion_tipo_criticidad__criticidad'
                ).get(id=obj_id)
                
                # Guardar la información antes de eliminar
                tipo_equipo = relacion.tipo_equipo
                tipo_equipo_id = tipo_equipo.id
                info = {
                    'tipo_equipo_name': tipo_equipo.name,
                    'producto_name': relacion.relacion_producto.producto.name,
                    'tipo_criticidad': relacion.relacion_producto.relacion_tipo_criticidad.tipo_criticidad.name,
                    'criticidad': relacion.relacion_producto.relacion_tipo_criticidad.criticidad.name
                }

                # Rastrear elementos que serán eliminados
                tecnologias_eliminadas = []
                tecnologias_actualizadas = []

                # 1. NIVEL TECNOLOGÍAS: Verificar tecnologías afectadas por esta relación
                tecnologias_con_esta_relacion = TecnologiaTipoEquipo.objects.filter(
                    relacion_tipo_equipo=relacion
                ).select_related('tecnologia', 'relacion_tipo_equipo')
                
                tecnologias_a_eliminar = set()
                for tech_rel in tecnologias_con_esta_relacion:
                    tecnologia = tech_rel.tecnologia
                    # Contar todas las relaciones de la tecnología
                    total_relaciones = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()
                    
                    # Si la tecnología solo tiene esta relación, se marcará para eliminación
                    if total_relaciones == 1:
                        tecnologias_a_eliminar.add(tecnologia)
                        tecnologias_eliminadas.append(tecnologia.name)
                    else:
                        tecnologias_actualizadas.append({
                            'nombre': tecnologia.name,
                            'relaciones_restantes': total_relaciones - 1
                        })

                # 2. Verificar si es la última relación del tipo de equipo
                total_relaciones = TipoEquipoProducto.objects.filter(tipo_equipo=tipo_equipo).count()
                was_last_relation = total_relaciones == 1
                
                mensaje_adicional = ""
                
                # 3. Realizar las eliminaciones
                if was_last_relation:
                    # Eliminar el tipo de equipo completo (esto eliminará la relación en cascada)
                    tipo_equipo.delete()
                else:
                    # Solo eliminar la relación específica
                    relacion.delete()

                # 4. Eliminar elementos huérfanos
                for tecnologia in tecnologias_a_eliminar:
                    tecnologia.delete()

                # 5. Construir mensaje detallado
                mensaje_detallado = ""
                if was_last_relation:
                    mensaje_detallado = f'Se ha eliminado el tipo de equipo "{info["tipo_equipo_name"]}" completamente ya que esta era su última asignación.\n\n'
                else:
                    mensaje_detallado = f'Se ha eliminado la relación del tipo de equipo "{info["tipo_equipo_name"]}".\n\n'
                
                mensaje_detallado += f'• Relación eliminada: {info["producto_name"]} ({info["tipo_criticidad"]} - {info["criticidad"]})\n'
                
                if tecnologias_eliminadas:
                    mensaje_detallado += f'• Tecnologías eliminadas: {", ".join(tecnologias_eliminadas)}\n'
                if tecnologias_actualizadas:
                    tech_act = [f"{t['nombre']} ({t['relaciones_restantes']} relaciones)" for t in tecnologias_actualizadas]
                    mensaje_detallado += f'• Tecnologías actualizadas: {", ".join(tech_act)}\n'
                
                mensaje_detallado += mensaje_adicional

                return Response({
                    'success': True,
                    'was_last_relation': was_last_relation,
                    'tipo_equipo_id': tipo_equipo_id,
                    'message': mensaje_detallado,
                    'detalles': {
                        'relacion_eliminada': f"{info['producto_name']} ({info['tipo_criticidad']} - {info['criticidad']})",
                        'tecnologias_eliminadas': tecnologias_eliminadas,
                        'tecnologias_actualizadas': [t['nombre'] for t in tecnologias_actualizadas]
                    }
                }, status=status.HTTP_200_OK)

        except TipoEquipoProducto.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No se encontró la relación especificada.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar la relación: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
