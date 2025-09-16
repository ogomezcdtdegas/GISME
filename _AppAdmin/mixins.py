# Mixins para permisos de administración
from rest_framework.response import Response
from rest_framework import status
from .utils import log_user_action, get_client_ip

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


class ActionLogMixin:
    """
    Mixin reutilizable para registrar acciones de usuario en el log de auditoría.
    
    Úsalo en cualquier vista que necesite logging de acciones:
    - Hereda de este mixin
    - Llama a self.log_action(...) con los datos relevantes
    
    Ejemplo de uso:
        class MiVistaConLogging(ActionLogMixin, MiVistaBase):
            def post(self, request, *args, **kwargs):
                response = super().post(request, *args, **kwargs)
                if response.status_code == 201:
                    self.log_action(
                        request=request,
                        action='crear',
                        affected_type='mi_tipo',
                        affected_value='valor_relevante',
                        affected_id=objeto_id
                    )
                return response
    """
    
    def log_action(self, request, action, affected_type, affected_value, affected_id):
        """
        Registrar una acción en el log de auditoría.
        
        Args:
            request: HttpRequest - Request de Django/DRF
            action: str - Acción realizada ('crear', 'editar', 'inactivar', 'activar')
            affected_type: str - Tipo de registro afectado ('ubicacion', 'sistema', 'usuario', etc.)
            affected_value: str - Valor representativo del registro (nombre, email, tag, etc.)
            affected_id: int/str - ID del registro afectado
        """
        try:
            log_user_action(
                user=request.user,
                action=action,
                affected_type=affected_type,
                affected_value=str(affected_value),
                affected_id=affected_id,
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            # No interrumpir el flujo principal si hay error en el logging
            print(f"Error en ActionLogMixin.log_action: {e}")
    
    def log_create_action(self, request, affected_type, affected_value, affected_id):
        """Helper para registrar acciones de creación"""
        self.log_action(request, 'crear', affected_type, affected_value, affected_id)
    
    def log_update_action(self, request, affected_type, affected_value, affected_id):
        """Helper para registrar acciones de edición"""
        self.log_action(request, 'editar', affected_type, affected_value, affected_id)
    
    def log_delete_action(self, request, affected_type, affected_value, affected_id):
        """Helper para registrar acciones de eliminación/inactivación"""
        self.log_action(request, 'inactivar', affected_type, affected_value, affected_id)
