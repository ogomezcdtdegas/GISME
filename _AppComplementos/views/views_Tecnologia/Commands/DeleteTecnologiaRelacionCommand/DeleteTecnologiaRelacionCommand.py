from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from repoGenerico.views_base import BaseDeleteView

from _AppComplementos.models import TecnologiaTipoEquipo, Tecnologia


class DeleteTecnologiaRelacionCommand(BaseDeleteView):
    """CBV Command para eliminar relación de tecnología usando BaseDeleteView"""
    model = TecnologiaTipoEquipo
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, **kwargs):
        """Override del método DELETE para lógica específica de eliminación"""
        try:
            # Extraer ID usando el método base
            obj_id = self._get_object_id_from_kwargs(kwargs)
            
            with transaction.atomic():
                # Buscar la relación específica
                relacion = self.model.objects.get(id=obj_id)
                tecnologia = relacion.tecnologia
                
                # Eliminar la relación
                relacion.delete()
                
                # Verificar si la tecnología queda huérfana
                relaciones_restantes = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()
                
                if relaciones_restantes == 0:
                    # Si no tiene más relaciones, eliminar la tecnología
                    nombre_tecnologia = tecnologia.name
                    tecnologia.delete()
                    
                    return Response({
                        'success': True,
                        'message': f'Relación eliminada. La tecnología "{nombre_tecnologia}" fue eliminada completamente al quedar sin relaciones.',
                        'tecnologia_eliminada': True
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': True,
                        'message': f'Relación eliminada. La tecnología "{tecnologia.name}" mantiene {relaciones_restantes} relación(es) restante(s).',
                        'tecnologia_eliminada': False
                    }, status=status.HTTP_200_OK)
                    
        except self.model.DoesNotExist:
            return Response({
                'success': False,
                'message': 'La relación no existe.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar la relación: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
