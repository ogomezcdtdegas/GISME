# Mixins para permisos de administración
from rest_framework.response import Response
from rest_framework import status

class AdminPermissionMixin:
    """Mixin para verificar permisos de administración de usuarios"""
    
    def check_admin_permission(self, user, action='access'):
        """
        Verificar permisos de administración
        
        Args:
            user: Usuario actual
            action: Tipo de acción ('access', 'create', 'update', 'delete')
        
        Returns:
            tuple: (has_permission: bool, error_response: Response|None)
        """
        if not hasattr(user, 'user_role') or not user.user_role:
            return False, Response({
                'success': False,
                'error': 'Usuario sin rol asignado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_role = user.user_role.role
        
        # Verificar acceso básico al módulo
        if action == 'access':
            if user_role in ['admin', 'admin_principal']:
                return True, None
            else:
                return False, Response({
                    'success': False,
                    'error': 'Su rol de usuario no tiene permisos para acceder al módulo de administración de usuarios.'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar permisos de modificación (create, update, delete)
        if action in ['create', 'update', 'delete']:
            if user_role == 'admin_principal':
                return True, None
            elif user_role == 'admin':
                return False, Response({
                    'success': False,
                    'error': 'Solo AdministradorPrincipal puede realizar esta operación'
                }, status=status.HTTP_403_FORBIDDEN)
            else:
                return False, Response({
                    'success': False,
                    'error': 'Su tipo de usuario no tiene permisos para realizar esta operación'
                }, status=status.HTTP_403_FORBIDDEN)
        
        return False, Response({
            'success': False,
            'error': 'Acción no reconocida'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch para verificar permisos antes de procesar"""
        # Determinar el tipo de acción basado en el método HTTP
        action_map = {
            'GET': 'access',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
        
        action = action_map.get(request.method, 'access')
        has_permission, error_response = self.check_admin_permission(request.user, action)
        
        if not has_permission:
            return error_response
        
        return super().dispatch(request, *args, **kwargs)
