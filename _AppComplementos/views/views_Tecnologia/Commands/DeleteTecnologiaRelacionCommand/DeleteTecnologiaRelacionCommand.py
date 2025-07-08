from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from _AppComplementos.models import TecnologiaTipoEquipo, Tecnologia

@method_decorator(csrf_exempt, name='dispatch')
class DeleteTecnologiaRelacionCommand(View):
    def delete(self, request, obj_id):
        try:
            with transaction.atomic():
                # Buscar la relación específica
                relacion = TecnologiaTipoEquipo.objects.get(id=obj_id)
                tecnologia = relacion.tecnologia
                
                # Eliminar la relación
                relacion.delete()
                
                # Verificar si la tecnología queda huérfana
                relaciones_restantes = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()
                
                if relaciones_restantes == 0:
                    # Si no tiene más relaciones, eliminar la tecnología
                    nombre_tecnologia = tecnologia.name
                    tecnologia.delete()
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Relación eliminada. La tecnología "{nombre_tecnologia}" fue eliminada completamente al quedar sin relaciones.',
                        'tecnologia_eliminada': True
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'message': f'Relación eliminada. La tecnología "{tecnologia.name}" mantiene {relaciones_restantes} relación(es) restante(s).',
                        'tecnologia_eliminada': False
                    })
                    
        except TecnologiaTipoEquipo.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'La relación no existe.'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar la relación: {str(e)}'
            }, status=500)
