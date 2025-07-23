from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Count
from _AppComplementos.models import (
    ProductoTipoCritCrit, Producto, TipoCriticidadCriticidad,
    TipoEquipo, TipoEquipoProducto,
    Tecnologia, TecnologiaTipoEquipo
)
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    delete=extend_schema(tags=['Producto']),
)

class DeleteProductoRelacionCommand(APIView):
    """CBV Command para eliminar relación de producto con lógica de cascada específica"""
    permission_classes = [IsAuthenticated]
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
                producto_id = producto.id
                info = {
                    'producto_name': producto.name,
                    'tipo_criticidad': relacion.relacion_tipo_criticidad.tipo_criticidad.name,
                    'criticidad': relacion.relacion_tipo_criticidad.criticidad.name
                }

                # Rastrear elementos que serán eliminados
                tipos_equipo_eliminados = []
                tipos_equipo_actualizados = []
                tecnologias_eliminadas = []
                tecnologias_actualizadas = []

                # 1. NIVEL TIPOS DE EQUIPO: Verificar tipos de equipo afectados por esta relación
                tipos_equipo_con_esta_relacion = TipoEquipoProducto.objects.filter(
                    relacion_producto=relacion
                ).select_related('tipo_equipo', 'relacion_producto')
                
                tipos_equipo_a_eliminar = set()
                for tipo_eq_rel in tipos_equipo_con_esta_relacion:
                    tipo_equipo = tipo_eq_rel.tipo_equipo
                    # Contar todas las relaciones del tipo de equipo
                    total_relaciones = TipoEquipoProducto.objects.filter(tipo_equipo=tipo_equipo).count()
                    
                    # Si el tipo de equipo solo tiene esta relación, se marcará para eliminación
                    if total_relaciones == 1:
                        tipos_equipo_a_eliminar.add(tipo_equipo)
                        tipos_equipo_eliminados.append(tipo_equipo.name)
                    else:
                        tipos_equipo_actualizados.append({
                            'nombre': tipo_equipo.name,
                            'relaciones_restantes': total_relaciones - 1
                        })

                # 2. NIVEL TECNOLOGÍAS: Verificar tecnologías afectadas
                tecnologias_con_estos_tipos = TecnologiaTipoEquipo.objects.filter(
                    relacion_tipo_equipo__in=tipos_equipo_con_esta_relacion
                ).select_related('tecnologia', 'relacion_tipo_equipo')
                
                tecnologias_a_eliminar = set()
                for tech_rel in tecnologias_con_estos_tipos:
                    tecnologia = tech_rel.tecnologia
                    # Contar todas las relaciones de la tecnología
                    total_relaciones = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()
                    # Contar relaciones con tipos de equipo que serán eliminados
                    relaciones_con_tipos_eliminados = TecnologiaTipoEquipo.objects.filter(
                        tecnologia=tecnologia,
                        relacion_tipo_equipo__tipo_equipo__in=tipos_equipo_a_eliminar
                    ).count()
                    
                    if total_relaciones == relaciones_con_tipos_eliminados:
                        tecnologias_a_eliminar.add(tecnologia)
                        tecnologias_eliminadas.append(tecnologia.name)
                    else:
                        tecnologias_actualizadas.append({
                            'nombre': tecnologia.name,
                            'relaciones_restantes': total_relaciones - relaciones_con_tipos_eliminados
                        })

                # 3. Verificar si es la última relación del producto
                total_relaciones = ProductoTipoCritCrit.objects.filter(producto=producto).count()
                was_last_relation = total_relaciones == 1
                
                # 4. Verificar si es la última relación con este tipo de criticidad
                tipo_criticidad = relacion.relacion_tipo_criticidad.tipo_criticidad
                total_relaciones_tipo = TipoCriticidadCriticidad.objects.filter(
                    tipo_criticidad=tipo_criticidad
                ).count()

                mensaje_adicional = ""
                
                # 5. Realizar las eliminaciones
                if was_last_relation:
                    # Eliminar el producto completo (esto eliminará la relación en cascada)
                    producto.delete()
                    if total_relaciones_tipo == 1:
                        tipo_criticidad.delete()
                        mensaje_adicional = f'\nAdemás, como era la última relación del tipo de criticidad "{info["tipo_criticidad"]}", este también ha sido eliminado del sistema.'
                else:
                    # Solo eliminar la relación específica
                    relacion.delete()

                # 6. Eliminar elementos huérfanos
                for tipo_equipo in tipos_equipo_a_eliminar:
                    tipo_equipo.delete()
                
                for tecnologia in tecnologias_a_eliminar:
                    tecnologia.delete()

                # 7. Construir mensaje detallado
                mensaje_detallado = ""
                if was_last_relation:
                    mensaje_detallado = f'Se ha eliminado el producto "{info["producto_name"]}" completamente ya que esta era su última asignación.\n\n'
                else:
                    mensaje_detallado = f'Se ha eliminado la relación del producto "{info["producto_name"]}".\n\n'
                
                mensaje_detallado += f'• Relación eliminada: {info["tipo_criticidad"]} - {info["criticidad"]}\n'
                
                if tipos_equipo_eliminados:
                    mensaje_detallado += f'• Tipos de equipo eliminados: {", ".join(tipos_equipo_eliminados)}\n'
                if tipos_equipo_actualizados:
                    tipos_act = [f"{t['nombre']} ({t['relaciones_restantes']} relaciones)" for t in tipos_equipo_actualizados]
                    mensaje_detallado += f'• Tipos de equipo actualizados: {", ".join(tipos_act)}\n'
                    
                if tecnologias_eliminadas:
                    mensaje_detallado += f'• Tecnologías eliminadas: {", ".join(tecnologias_eliminadas)}\n'
                if tecnologias_actualizadas:
                    tech_act = [f"{t['nombre']} ({t['relaciones_restantes']} relaciones)" for t in tecnologias_actualizadas]
                    mensaje_detallado += f'• Tecnologías actualizadas: {", ".join(tech_act)}\n'
                
                mensaje_detallado += mensaje_adicional

                return Response({
                    'success': True,
                    'was_last_relation': was_last_relation,
                    'producto_id': producto_id,
                    'message': mensaje_detallado,
                    'detalles': {
                        'relacion_eliminada': f"{info['tipo_criticidad']} - {info['criticidad']}",
                        'tipos_equipo_eliminados': tipos_equipo_eliminados,
                        'tipos_equipo_actualizados': [t['nombre'] for t in tipos_equipo_actualizados],
                        'tecnologias_eliminadas': tecnologias_eliminadas,
                        'tecnologias_actualizadas': [t['nombre'] for t in tecnologias_actualizadas]
                    }
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
