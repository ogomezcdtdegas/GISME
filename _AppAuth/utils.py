"""
Utilidades para manejo centralizado de roles y permisos de usuario
"""
from django.contrib.auth.mixins import LoginRequiredMixin


def get_user_role_context(user):
    """
    Obtiene el contexto de rol y permisos para un usuario
    
    Args:
        user: Usuario autenticado
        
    Returns:
        dict: Contexto con información de rol y permisos
    """
    user_role = None
    if hasattr(user, 'user_role') and user.user_role:
        user_role = user.user_role.role

    # Configurar flags de permisos básicos
    permissions = {
        'current_user_role': user_role,
        'is_authenticated': user.is_authenticated,
        
        # Roles específicos
        'is_supervisor': user_role == 'supervisor',
        'is_admin': user_role == 'admin', 
        'is_admin_principal': user_role == 'admin_principal',
        
        # Permisos administrativos
        'can_access_admin': user_role in ['admin', 'admin_principal'],
        'can_create_users': user_role == 'admin_principal',
        'can_edit_users': user_role == 'admin_principal',
        'can_delete_users': user_role == 'admin_principal',
        
        # Control de acceso general
        'access_denied': False,
        'access_denied_message': '',
        
        # Permisos para otras funcionalidades (expandible)
        'can_access_monitoring': user_role in ['admin', 'admin_principal', 'supervisor'],
        'can_access_tools': user_role in ['admin', 'admin_principal', 'supervisor'],
        'can_access_calculations': user_role in ['admin', 'admin_principal', 'supervisor'],
        'can_manage_equipment': user_role in ['admin', 'admin_principal'],
        'can_access_complementos': user_role in ['admin', 'admin_principal'],  # Supervisor NO tiene acceso
    }
    
    # Configurar mensajes de acceso denegado específicos
    if user_role == 'supervisor':
        # Supervisor tiene acceso limitado a algunas secciones
        pass  # No hay acceso denegado general, pero sí para admin
    elif user_role not in ['admin', 'admin_principal', 'supervisor']:
        permissions['access_denied'] = True
        permissions['access_denied_message'] = 'Su rol de usuario no tiene permisos para acceder a esta sección.'
    
    return permissions


def get_admin_context(user):
    """
    Contexto específico para módulo de administración
    
    Args:
        user: Usuario autenticado
        
    Returns:
        dict: Contexto con permisos específicos para administración
    """
    base_context = get_user_role_context(user)
    user_role = base_context.get('current_user_role')
    
    # Configuración específica para administración
    admin_context = {
        'access_denied': False,
        'access_denied_message': '',
    }
    
    if user_role == 'supervisor':
        admin_context.update({
            'access_denied': True,
            'access_denied_message': 'Su tipo de usuario Supervisor no tiene permiso de acceso. Solo Administradores.'
        })
    elif user_role not in ['admin', 'admin_principal']:
        admin_context.update({
            'access_denied': True,
            'access_denied_message': 'Su rol de usuario no tiene permisos para acceder al módulo de administración de usuarios.'
        })
    
    # Combinar contextos
    base_context.update(admin_context)
    return base_context


def get_monitoring_context(user):
    """
    Contexto específico para módulo de monitoreo Coriolis
    
    Args:
        user: Usuario autenticado
        
    Returns:
        dict: Contexto con permisos específicos para monitoreo
    """
    base_context = get_user_role_context(user)
    user_role = base_context.get('current_user_role')
    
    # Configuración específica para monitoreo Coriolis
    monitoring_context = {
        'access_denied': False,
        'access_denied_message': '',
        
        # Permisos específicos para configuración de constantes/coeficientes
        'can_configure_constants': user_role in ['admin', 'admin_principal'],
        'can_view_batch_detection': user_role in ['admin', 'admin_principal', 'supervisor'],
        'can_modify_batch_detection': user_role in ['admin', 'admin_principal'],
        'can_assign_tickets': user_role in ['admin', 'admin_principal', 'supervisor'],
        
        # Configuración de acceso
        'show_config_buttons': user_role in ['admin', 'admin_principal'],
        'readonly_config_view': user_role == 'supervisor',
    }
    
    # Verificar acceso general al monitoreo
    if user_role not in ['admin', 'admin_principal', 'supervisor']:
        monitoring_context.update({
            'access_denied': True,
            'access_denied_message': 'Su rol de usuario no tiene permisos para acceder al módulo de monitoreo Coriolis.'
        })
    
    # Combinar contextos
    base_context.update(monitoring_context)
    return base_context


class UserRoleContextMixin:
    """
    Mixin para agregar contexto de rol de usuario automáticamente a las vistas
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar contexto de rol y permisos
        if hasattr(self.request, 'user'):
            context.update(get_user_role_context(self.request.user))
        
        return context


class AdminContextMixin:
    """
    Mixin específico para vistas de administración
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar contexto específico de administración
        if hasattr(self.request, 'user'):
            context.update(get_admin_context(self.request.user))
        
        return context


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin para requerir roles específicos en vistas
    """
    required_roles = []  # Lista de roles permitidos ['admin', 'admin_principal']
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar autenticación primero
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Verificar rol
        user_role = None
        if hasattr(request.user, 'user_role') and request.user.user_role:
            user_role = request.user.user_role.role
        
        if self.required_roles and user_role not in self.required_roles:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("No tiene permisos para acceder a esta página.")
        
        return super().dispatch(request, *args, **kwargs)
