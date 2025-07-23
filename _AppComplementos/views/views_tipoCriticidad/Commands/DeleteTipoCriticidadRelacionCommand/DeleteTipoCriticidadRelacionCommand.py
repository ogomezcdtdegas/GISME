from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Count
from _AppComplementos.models import (
    TipoCriticidadCriticidad, 
    ProductoTipoCritCrit, Producto,
    TipoEquipoProducto, TipoEquipo,
    TecnologiaTipoEquipo, Tecnologia
)

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    delete=extend_schema(tags=['TipoCriticidad']),
)

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

                # Rastrear elementos que serán eliminados
                productos_eliminados = []
                productos_actualizados = []
                tipos_equipo_eliminados = []
                tipos_equipo_actualizados = []
                tecnologias_eliminadas = []
                tecnologias_actualizadas = []

                # 1. NIVEL PRODUCTOS: Identificar productos afectados
                productos_con_esta_relacion = ProductoTipoCritCrit.objects.filter(
                    relacion_tipo_criticidad=relacion
                ).select_related('producto')
                
                productos_a_eliminar = set()
                for prod_rel in productos_con_esta_relacion:
                    producto = prod_rel.producto
                    # Contar todas las relaciones de este producto
                    total_relaciones_producto = ProductoTipoCritCrit.objects.filter(
                        producto=producto
                    ).count()
                    
                    # Si el producto solo tiene esta relación, se marcará para eliminación
                    if total_relaciones_producto == 1:
                        productos_a_eliminar.add(producto)
                        productos_eliminados.append(producto.name)
                    else:
                        productos_actualizados.append({
                            'nombre': producto.name,
                            'relaciones_restantes': total_relaciones_producto - 1
                        })

                # 2. NIVEL TIPOS DE EQUIPO: Verificar tipos de equipo afectados
                tipos_equipo_con_estos_productos = TipoEquipoProducto.objects.filter(
                    relacion_producto__in=productos_con_esta_relacion
                ).select_related('tipo_equipo', 'relacion_producto')
                
                tipos_equipo_a_eliminar = set()
                for tipo_eq_rel in tipos_equipo_con_estos_productos:
                    tipo_equipo = tipo_eq_rel.tipo_equipo
                    # Contar todas las relaciones del tipo de equipo
                    total_relaciones = TipoEquipoProducto.objects.filter(tipo_equipo=tipo_equipo).count()
                    # Contar relaciones con productos que serán eliminados
                    relaciones_con_productos_eliminados = TipoEquipoProducto.objects.filter(
                        tipo_equipo=tipo_equipo,
                        relacion_producto__producto__in=productos_a_eliminar
                    ).count()
                    
                    if total_relaciones == relaciones_con_productos_eliminados:
                        tipos_equipo_a_eliminar.add(tipo_equipo)
                        tipos_equipo_eliminados.append(tipo_equipo.name)
                    else:
                        tipos_equipo_actualizados.append({
                            'nombre': tipo_equipo.name,
                            'relaciones_restantes': total_relaciones - relaciones_con_productos_eliminados
                        })

                # 3. NIVEL TECNOLOGÍAS: Verificar tecnologías afectadas
                tecnologias_con_estos_tipos = TecnologiaTipoEquipo.objects.filter(
                    relacion_tipo_equipo__in=tipos_equipo_con_estos_productos
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

                # 4. Verificar si es la última relación del tipo de criticidad
                total_relaciones = TipoCriticidadCriticidad.objects.filter(
                    tipo_criticidad=tipo_criticidad
                ).count()
                was_last_relation = total_relaciones == 1

                # 5. Realizar las eliminaciones
                if was_last_relation:
                    # Si es la última relación del tipo, eliminar el tipo completo
                    tipo_criticidad.delete()  # Esto eliminará en cascada todas las relaciones
                else:
                    # Solo eliminar la relación específica
                    relacion.delete()

                # 6. Eliminar elementos huérfanos
                for producto in productos_a_eliminar:
                    producto.delete()
                
                for tipo_equipo in tipos_equipo_a_eliminar:
                    tipo_equipo.delete()
                
                for tecnologia in tecnologias_a_eliminar:
                    tecnologia.delete()

                # 7. Construir mensaje detallado
                mensaje_detallado = ""
                if was_last_relation:
                    mensaje_detallado = f'Se ha eliminado el tipo de criticidad "{info["tipo_criticidad"]}" completamente ya que esta era su última relación.\n\n'
                else:
                    mensaje_detallado = f'Se ha eliminado la relación del tipo de criticidad "{info["tipo_criticidad"]}".\n\n'
                
                mensaje_detallado += f'• Criticidad afectada: {info["criticidad"]}\n'
                
                if productos_eliminados:
                    mensaje_detallado += f'• Productos eliminados: {", ".join(productos_eliminados)}\n'
                if productos_actualizados:
                    productos_act = [f"{p['nombre']} ({p['relaciones_restantes']} relaciones)" for p in productos_actualizados]
                    mensaje_detallado += f'• Productos actualizados: {", ".join(productos_act)}\n'
                    
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
                    'was_last_relation': was_last_relation,
                    'tipo_criticidad_id': tipo_criticidad_id,
                    'message': mensaje_detallado,
                    'detalles': {
                        'criticidad_afectada': info["criticidad"],
                        'productos_eliminados': productos_eliminados,
                        'productos_actualizados': [p['nombre'] for p in productos_actualizados],
                        'tipos_equipo_eliminados': tipos_equipo_eliminados,
                        'tipos_equipo_actualizados': [t['nombre'] for t in tipos_equipo_actualizados],
                        'tecnologias_eliminadas': tecnologias_eliminadas,
                        'tecnologias_actualizadas': [t['nombre'] for t in tecnologias_actualizadas]
                    }
                }, status=status.HTTP_200_OK)

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
                            # Separar la barra invertida de la f-string
                            linea_producto = f"• {prod_info['nombre']} (eliminado por quedar sin relaciones)"
                            mensaje_productos += f"{linea_producto}\n"
                        else:
                            # Separar la barra invertida de la f-string
                            linea_producto = f"• {prod_info['nombre']} (actualizado)"
                            mensaje_productos += f"{linea_producto}\n"

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
                        # Separar las barras invertidas de las f-strings
                        f'Se ha eliminado el tipo de criticidad "{info["tipo_criticidad"]}" completamente ya que esta era su última relación.\n\n'
                        if was_last_relation else
                        f'Se ha eliminado la relación del tipo de criticidad "{info["tipo_criticidad"]}".\n\n'
                    ) + (
                        'Se eliminó la siguiente relación:\n' +
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
