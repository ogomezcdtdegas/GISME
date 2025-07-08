from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Count, ProtectedError
from _AppComplementos.models import (
    TipoCriticidad, TipoCriticidadCriticidad, 
    ProductoTipoCritCrit, Producto,
    TipoEquipoProducto, TipoEquipo,
    TecnologiaTipoEquipo, Tecnologia
)

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
                relaciones_tipo_criticidad = TipoCriticidadCriticidad.objects.filter(
                    tipo_criticidad=tipo_criticidad
                ).select_related('criticidad')
                
                # Información para el resumen
                nombre_tipo = tipo_criticidad.name
                criticidades_relacionadas = [rel.criticidad.name for rel in relaciones_tipo_criticidad]
                
                # Rastrear elementos que serán eliminados
                productos_eliminados = []
                productos_actualizados = []
                tipos_equipo_eliminados = []
                tipos_equipo_actualizados = []
                tecnologias_eliminadas = []
                tecnologias_actualizadas = []
                
                # 1. NIVEL PRODUCTOS: Obtener todos los productos afectados
                productos_con_este_tipo = ProductoTipoCritCrit.objects.filter(
                    relacion_tipo_criticidad__tipo_criticidad=tipo_criticidad
                ).select_related('producto', 'relacion_tipo_criticidad')
                
                productos_a_eliminar = set()
                for prod_rel in productos_con_este_tipo:
                    producto = prod_rel.producto
                    # Contar todas las relaciones del producto
                    total_relaciones = ProductoTipoCritCrit.objects.filter(producto=producto).count()
                    # Contar relaciones con este tipo de criticidad
                    relaciones_con_este_tipo = ProductoTipoCritCrit.objects.filter(
                        producto=producto,
                        relacion_tipo_criticidad__tipo_criticidad=tipo_criticidad
                    ).count()
                    
                    if total_relaciones == relaciones_con_este_tipo:
                        productos_a_eliminar.add(producto)
                        productos_eliminados.append(producto.name)
                    else:
                        productos_actualizados.append({
                            'nombre': producto.name,
                            'relaciones_restantes': total_relaciones - relaciones_con_este_tipo
                        })
                
                # 2. NIVEL TIPOS DE EQUIPO: Verificar tipos de equipo afectados
                tipos_equipo_con_estos_productos = TipoEquipoProducto.objects.filter(
                    relacion_producto__in=productos_con_este_tipo
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
                
                # 4. ELIMINACIÓN EN CASCADA (Django se encarga de las relaciones)
                # Al eliminar el tipo de criticidad, Django eliminará automáticamente:
                # - TipoCriticidadCriticidad (CASCADE)
                # - ProductoTipoCritCrit (CASCADE desde TipoCriticidadCriticidad)
                # - TipoEquipoProducto (CASCADE desde ProductoTipoCritCrit)
                # - TecnologiaTipoEquipo (CASCADE desde TipoEquipoProducto)
                tipo_criticidad.delete()
                
                # 5. Eliminar elementos huérfanos
                for producto in productos_a_eliminar:
                    producto.delete()
                
                for tipo_equipo in tipos_equipo_a_eliminar:
                    tipo_equipo.delete()
                
                for tecnologia in tecnologias_a_eliminar:
                    tecnologia.delete()
                
                # 6. Construir mensaje detallado
                mensaje_detallado = f'Se ha eliminado el tipo de criticidad "{nombre_tipo}" y todas sus relaciones:\n\n'
                mensaje_detallado += f'• Criticidades relacionadas: {", ".join(criticidades_relacionadas)}\n'
                
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
                    'message': mensaje_detallado,
                    'detalles': {
                        'criticidades_relacionadas': criticidades_relacionadas,
                        'productos_eliminados': productos_eliminados,
                        'productos_actualizados': [p['nombre'] for p in productos_actualizados],
                        'tipos_equipo_eliminados': tipos_equipo_eliminados,
                        'tipos_equipo_actualizados': [t['nombre'] for t in tipos_equipo_actualizados],
                        'tecnologias_eliminadas': tecnologias_eliminadas,
                        'tecnologias_actualizadas': [t['nombre'] for t in tecnologias_actualizadas]
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
