from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db import transaction

from _AppComplementos.models import TipoEquipo, TipoEquipoProducto


@method_decorator(csrf_exempt, name='dispatch')
class DeleteTipoEquipoCommand(View):
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Obtener la relación a eliminar
                tipo_equipo_producto = get_object_or_404(TipoEquipoProducto, id=obj_id)
                tipo_equipo = tipo_equipo_producto.tipo_equipo
                
                # Contar cuántas relaciones tiene este tipo de equipo
                relaciones_count = TipoEquipoProducto.objects.filter(tipo_equipo=tipo_equipo).count()
                
                # Eliminar la relación
                tipo_equipo_producto.delete()
                
                # Si era la última relación, eliminar también el tipo de equipo
                if relaciones_count == 1:
                    tipo_equipo.delete()
                    message = f'Tipo de equipo "{tipo_equipo.name}" eliminado completamente (era su última relación)'
                    was_last_relation = True
                else:
                    message = f'Relación del tipo de equipo "{tipo_equipo.name}" eliminada correctamente'
                    was_last_relation = False
                
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'was_last_relation': was_last_relation
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteTipoEquipoRelacionCommand(View):
    def delete(self, request, obj_id):
        try:
            # Obtener la relación a eliminar
            tipo_equipo_producto = get_object_or_404(TipoEquipoProducto, id=obj_id)
            
            # Eliminar solo la relación, manteniendo el tipo de equipo
            tipo_equipo_producto.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Relación eliminada correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar la relación: {str(e)}'
            }, status=500)
