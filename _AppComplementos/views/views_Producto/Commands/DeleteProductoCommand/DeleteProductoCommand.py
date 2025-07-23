from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import ProtectedError
from _AppComplementos.models import (
    Producto, ProductoTipoCritCrit,
    TipoEquipo, TipoEquipoProducto,
    Tecnologia, TecnologiaTipoEquipo
)
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    delete=extend_schema(tags=['Producto']),
)

class DeleteProductoCommand(APIView):
    """CBV Command para eliminar producto con lógica de cascada específica"""
    permission_classes = [IsAuthenticated]
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Obtener el producto
                producto = Producto.objects.get(id=obj_id)
                
                # Obtener las relaciones antes de eliminar para mostrar el resumen
                relaciones_producto = ProductoTipoCritCrit.objects.filter(
                    producto=producto
                ).select_related('relacion_tipo_criticidad__tipo_criticidad', 'relacion_tipo_criticidad__criticidad')
                
                # Información para el resumen
                nombre_producto = producto.name
                asignaciones_criticidad = [
                    f"{rel.relacion_tipo_criticidad.tipo_criticidad.name} - {rel.relacion_tipo_criticidad.criticidad.name}"
                    for rel in relaciones_producto
                ]
                
                # Rastrear elementos que serán eliminados
                tipos_equipo_eliminados = []
                tipos_equipo_actualizados = []
                tecnologias_eliminadas = []
                tecnologias_actualizadas = []
                
                # 1. NIVEL TIPOS DE EQUIPO: Verificar tipos de equipo afectados
                tipos_equipo_con_este_producto = TipoEquipoProducto.objects.filter(
                    relacion_producto__in=relaciones_producto
                ).select_related('tipo_equipo', 'relacion_producto')
                
                tipos_equipo_a_eliminar = set()
                for tipo_eq_rel in tipos_equipo_con_este_producto:
                    tipo_equipo = tipo_eq_rel.tipo_equipo
                    # Contar todas las relaciones del tipo de equipo
                    total_relaciones = TipoEquipoProducto.objects.filter(tipo_equipo=tipo_equipo).count()
                    # Contar relaciones con este producto
                    relaciones_con_este_producto = TipoEquipoProducto.objects.filter(
                        tipo_equipo=tipo_equipo,
                        relacion_producto__producto=producto
                    ).count()
                    
                    if total_relaciones == relaciones_con_este_producto:
                        tipos_equipo_a_eliminar.add(tipo_equipo)
                        tipos_equipo_eliminados.append(tipo_equipo.name)
                    else:
                        tipos_equipo_actualizados.append({
                            'nombre': tipo_equipo.name,
                            'relaciones_restantes': total_relaciones - relaciones_con_este_producto
                        })
                
                # 2. NIVEL TECNOLOGÍAS: Verificar tecnologías afectadas
                tecnologias_con_estos_tipos = TecnologiaTipoEquipo.objects.filter(
                    relacion_tipo_equipo__in=tipos_equipo_con_este_producto
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
                
                # 3. ELIMINACIÓN EN CASCADA (Django se encarga de las relaciones)
                # Al eliminar el producto, Django eliminará automáticamente:
                # - ProductoTipoCritCrit (CASCADE)
                # - TipoEquipoProducto (CASCADE desde ProductoTipoCritCrit)
                # - TecnologiaTipoEquipo (CASCADE desde TipoEquipoProducto)
                producto.delete()
                
                # 4. Eliminar elementos huérfanos
                for tipo_equipo in tipos_equipo_a_eliminar:
                    tipo_equipo.delete()
                
                for tecnologia in tecnologias_a_eliminar:
                    tecnologia.delete()
                
                # 5. Construir mensaje detallado
                mensaje_detallado = f'Se ha eliminado el producto "{nombre_producto}" y todas sus relaciones:\n\n'
                
                if asignaciones_criticidad:
                    asignaciones_texto = ", ".join(asignaciones_criticidad)
                    mensaje_detallado += f'• Asignaciones de criticidad eliminadas: {asignaciones_texto}\n'
                    
                if tipos_equipo_eliminados:
                    mensaje_detallado += f'• Tipos de equipo eliminados: {", ".join(tipos_equipo_eliminados)}\n'
                if tipos_equipo_actualizados:
                    tipos_act = [f"{t['nombre']} ({t['relaciones_restantes']} relaciones)" for t in tipos_equipo_actualizados]
                    mensaje_detallado += f'• Tipos de equipo actualizados: {", ".join(tipos_act)}\n'
                    
                if tecnologias_eliminadas:
                    mensaje_detallado += f'• Tecnologías eliminadas: {", ".join(tecnologias_eliminadas)}\n'
                if tecnologias_actualizadas:
                    tech_act = [f"{t['nombre']} ({t['relaciones_restantes']} relaciones)" for t in tecnologias_actualizadas]
                    mensaje_detallado += f'• Tecnologías actualizadas: {", ".join(tech_act)}'
                
                return Response({
                    'success': True,
                    'message': mensaje_detallado,
                    'detalles': {
                        'asignaciones_eliminadas': asignaciones_criticidad,
                        'tipos_equipo_eliminados': tipos_equipo_eliminados,
                        'tipos_equipo_actualizados': [t['nombre'] for t in tipos_equipo_actualizados],
                        'tecnologias_eliminadas': tecnologias_eliminadas,
                        'tecnologias_actualizadas': [t['nombre'] for t in tecnologias_actualizadas]
                    }
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
