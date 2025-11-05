from django.contrib.auth.models import User
from django.http import JsonResponse
from repoGenerico.views_base import BaseDeleteView
from ....mixins import AdminPermissionMixin

class DeleteAdminUserCommand(AdminPermissionMixin, BaseDeleteView):
    """Command para eliminar usuarios administrativos"""
    model = User
    
    def delete(self, request, **kwargs):
        """Override para validaciones adicionales antes de eliminar"""
        try:
            # Obtener ID del usuario usando el método base
            obj_id = self._get_object_id_from_kwargs(kwargs)
            user_to_delete = self.model.objects.get(id=obj_id)
            
            # Validación: No permitir auto-eliminación
            if user_to_delete == request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'No puedes eliminarte a ti mismo'
                }, status=400)
            
            # Llamar al método base para realizar la eliminación
            return super().delete(request, **kwargs)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar usuario: {str(e)}'
            }, status=500)
