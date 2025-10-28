# Mixins para permisos de administración
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from .utils import log_user_action, get_client_ip

class ComplementosPermissionMixin:
    """Mixin para verificar permisos de acceso a módulos de complementos (ubicaciones, sistemas)"""
    
    def check_complementos_permission(self, user, action='access'):
        """
        Verificar permisos para módulos de complementos
        
        Args:
            user: Usuario actual
            action: Tipo de acción ('access', 'create', 'update', 'delete')
        
        Returns:
            tuple: (has_permission: bool, error_response: Response|None)
        """
        # Superuser siempre tiene acceso
        if user.is_superuser:
            return True, None
            
        if not hasattr(user, 'user_role') or not user.user_role:
            return False, None  # Indicar que no tiene permisos
        
        user_role = user.user_role.role
        
        # Solo admin y admin_principal pueden acceder a complementos
        if user_role in ['admin', 'admin_principal']:
            return True, None
        else:
            return False, None  # Indicar que no tiene permisos
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch para verificar permisos antes de procesar"""
        has_permission, _ = self.check_complementos_permission(request.user)
        
        if not has_permission:
            # Si es una request que espera JSON (API), devolver error JSON
            if request.content_type == 'application/json' or 'api' in request.path or request.headers.get('Accept', '').startswith('application/json'):
                return Response({
                    'success': False,
                    'error': 'Su rol de usuario no tiene permisos para acceder a este módulo.'
                }, status=status.HTTP_403_FORBIDDEN)
            # Si es una vista de template, redirigir al home
            else:
                return redirect('/')
        
        return super().dispatch(request, *args, **kwargs)


class SuperuserPermissionMixin:
    """Mixin para verificar que solo superusers puedan realizar ciertas acciones"""
    
    def check_superuser_permission(self, user, action='delete'):
        """
        Verificar permisos de superuser para acciones críticas
        
        Args:
            user: Usuario actual
            action: Tipo de acción ('delete', 'critical')
        
        Returns:
            tuple: (has_permission: bool, error_response: Response|None)
        """
        if not user.is_superuser:
            return False, Response({
                'success': False,
                'error': 'Solo superusuarios pueden realizar esta operación'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return True, None
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch para verificar permisos de superuser antes de procesar"""
        if request.method == 'DELETE':
            has_permission, error_response = self.check_superuser_permission(request.user)
            
            if not has_permission:
                return error_response
        
        return super().dispatch(request, *args, **kwargs)


class AdminPermissionMixin:
    """Mixin para verificar permisos de administración de usuarios"""
    
    def check_admin_permission(self, user, action='access'):
        """
        Verificar permisos de administración
        
        Args:
            user: Usuario actual
            action: Tipo de acción ('access', 'create', 'update', 'delete')
        
        Returns:
            tuple: (has_permission: bool, action_denied_reason: str|None)
        """
        # Superuser siempre tiene acceso
        if user.is_superuser:
            return True, None
            
        if not hasattr(user, 'user_role') or not user.user_role:
            return False, 'Usuario sin rol asignado'
        
        user_role = user.user_role.role
        
        # Verificar acceso básico al módulo
        if action == 'access':
            if user_role in ['admin', 'admin_principal']:
                return True, None
            else:
                return False, 'Su rol de usuario no tiene permisos para acceder al módulo de administración de usuarios.'
        
        # Verificar permisos de modificación (create, update, delete)
        if action in ['create', 'update', 'delete']:
            if user_role == 'admin_principal':
                return True, None
            elif user_role == 'admin':
                return False, 'Solo AdministradorPrincipal puede realizar esta operación'
            else:
                return False, 'Su tipo de usuario no tiene permisos para realizar esta operación'
        
        return False, 'Acción no reconocida'
    
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
        has_permission, error_message = self.check_admin_permission(request.user, action)
        
        if not has_permission:
            # Si es una request que espera JSON (API), devolver error JSON
            if request.content_type == 'application/json' or 'api' in request.path or request.headers.get('Accept', '').startswith('application/json'):
                return Response({
                    'success': False,
                    'error': error_message
                }, status=status.HTTP_403_FORBIDDEN)
            # Si es una vista de template, redirigir al home
            else:
                return redirect('/')
        
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


class UniversalActionLogMixin:
    """
    Mixin universal que automáticamente registra acciones CRUD
    Solo necesitas definir: log_config
    
    Ejemplo de uso:
        class CreateUbicacionWithLogging(UniversalActionLogMixin, CreateUbicacionView):
            log_config = {
                'affected_type': 'ubicacion',
                'get_value': lambda obj: obj.nombre,
                'model_class': Ubicacion,
            }
    """
    
    log_config = {
        'affected_type': None,  # 'usuario', 'ubicacion', 'sistema'
        'get_value': None,      # lambda obj: obj.email, lambda obj: obj.nombre, etc.
        'model_class': None,    # User, Ubicacion, Sistema
    }
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self._log_if_successful(request, response, 'crear', args, kwargs)
        return response
    
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        self._log_if_successful(request, response, 'editar', args, kwargs)
        return response
    
    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        self._log_if_successful(request, response, 'editar', args, kwargs)
        return response
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        self._log_if_successful(request, response, 'inactivar', args, kwargs)
        return response
    
    def _log_if_successful(self, request, response, action, args, kwargs):
        """Registra la acción si fue exitosa"""
        
        if not self._is_successful_response(response, action):
            return
        
        try:
            obj, obj_id = self._get_object_and_id(response, action, args, kwargs)
            if obj and obj_id:
                affected_value = self.log_config['get_value'](obj)
                
                log_user_action(
                    user=request.user,
                    action=action,
                    affected_type=self.log_config['affected_type'],
                    affected_value=affected_value,
                    affected_id=str(obj_id),
                    ip_address=get_client_ip(request)
                )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error logging {action}: {e}")
    
    def _is_successful_response(self, response, action):
        """Verifica si la respuesta fue exitosa"""
        if not hasattr(response, 'status_code'):
            return False
        return (action == 'crear' and response.status_code == 201) or \
               (action in ['editar', 'inactivar'] and response.status_code == 200)
    
    def _get_object_and_id(self, response, action, args, kwargs):
        """Obtiene el objeto y su ID según la acción"""
        obj_id = None
        
        if action == 'crear':
            # Para crear, intentar obtener el ID de la respuesta
            if hasattr(response, 'data') and isinstance(response.data, dict):
                obj_id = response.data.get('id')
            # Si no está en data, intentar con response directamente si es dict
            elif isinstance(response, dict):
                obj_id = response.get('id')
        else:
            # Para editar/eliminar, obtener ID de kwargs o args
            obj_id = kwargs.get('pk') or kwargs.get('user_id') or kwargs.get('obj_id')
            
            # Si no se encontró, buscar cualquier parámetro que termine en '_id'
            if not obj_id:
                for key, value in kwargs.items():
                    if key.endswith('_id') and value:
                        obj_id = value
                        break
            
            # Como último recurso, intentar con args
            if not obj_id and args:
                obj_id = args[0] if args else None
        
        if obj_id and self.log_config['model_class']:
            try:
                obj = self.log_config['model_class'].objects.get(id=obj_id)
                return obj, obj_id
            except Exception as e:
                return None, None
        
        return None, None
