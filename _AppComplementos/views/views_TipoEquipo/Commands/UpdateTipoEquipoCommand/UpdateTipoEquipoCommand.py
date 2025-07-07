from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
import json

from _AppComplementos.models import TipoEquipo, TipoEquipoProducto, ProductoTipoCritCrit
from _AppComplementos.serializers import TipoEquipoProductoSerializer


@method_decorator(csrf_exempt, name='dispatch')
class EditarTipoEquipoView(View):
    def put(self, request, obj_id):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            producto_id = data.get('producto_id')
            tipo_criticidad_id = data.get('tipo_criticidad_id')
            criticidad_id = data.get('criticidad_id')
            
            # Validar que todos los campos estén presentes
            if not all([name, producto_id, tipo_criticidad_id, criticidad_id]):
                return JsonResponse({
                    'success': False,
                    'error': 'Todos los campos son obligatorios'
                }, status=400)
            
            # Obtener la relación a actualizar
            tipo_equipo_producto = get_object_or_404(TipoEquipoProducto, id=obj_id)
            
            # Buscar la relación ProductoTipoCritCrit basándose en los IDs
            producto_relacion = ProductoTipoCritCrit.objects.filter(
                producto_id=producto_id,
                relacion_tipo_criticidad__tipo_criticidad_id=tipo_criticidad_id,
                relacion_tipo_criticidad__criticidad_id=criticidad_id
            ).first()

            if not producto_relacion:
                return JsonResponse({
                    'success': False,
                    'error': 'La combinación de producto, tipo de criticidad y criticidad no existe'
                }, status=400)
            
            # Obtener el tipo de equipo actual
            tipo_equipo_actual = tipo_equipo_producto.tipo_equipo
            
            # Si el nombre cambió, verificar que no exista otro TipoEquipo con ese nombre
            if tipo_equipo_actual.name != name:
                if TipoEquipo.objects.filter(name=name).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'Ya existe un tipo de equipo con el nombre "{name}"'
                    }, status=400)
                
                # Actualizar el nombre del tipo de equipo existente
                tipo_equipo_actual.name = name
                tipo_equipo_actual.save()
            
            # Verificar si ya existe esta combinación (excluyendo el registro actual)
            if TipoEquipoProducto.objects.filter(
                tipo_equipo=tipo_equipo_actual,
                relacion_producto=producto_relacion
            ).exclude(id=obj_id).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Esta combinación ya existe'
                }, status=400)
            
            # Actualizar la relación
            tipo_equipo_producto.tipo_equipo = tipo_equipo_actual
            tipo_equipo_producto.relacion_producto = producto_relacion
            tipo_equipo_producto.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Tipo de equipo actualizado correctamente',
                'data': TipoEquipoProductoSerializer(tipo_equipo_producto).data
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Error en el formato de datos'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)
