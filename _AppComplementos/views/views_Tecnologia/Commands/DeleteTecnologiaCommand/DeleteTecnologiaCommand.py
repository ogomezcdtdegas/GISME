from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .....models import TecnologiaTipoEquipo
from django.http import JsonResponse

class DeleteTecnologiaCommand(APIView):
    
    def delete(self, request, obj_id):
        try:
            relacion = TecnologiaTipoEquipo.objects.get(id=obj_id)
            tecnologia_name = relacion.tecnologia.name
            relacion.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Relación de tecnología "{tecnologia_name}" eliminada correctamente'
            }, status=status.HTTP_200_OK)
            
        except TecnologiaTipoEquipo.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'La relación de tecnología no existe'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar la relación: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
