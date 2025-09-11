from django.http import JsonResponse
from django.views import View
from ....models import UserRole
from ....mixins import AdminPermissionMixin

class GetAdminRolesQuery(AdminPermissionMixin, View):
    """Query para obtener roles disponibles"""
    
    def get(self, request):
        try:
            roles = [
                {'value': choice[0], 'label': choice[1]} 
                for choice in UserRole.ROLE_CHOICES
            ]
            return JsonResponse({
                'success': True, 
                'roles': roles
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al obtener roles: {str(e)}'
            }, status=500)
