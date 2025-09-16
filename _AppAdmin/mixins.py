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
        print(f"🚀 UniversalActionLogMixin.post() llamado")
        print(f"   - self.__class__: {self.__class__}")
        print(f"   - MRO: {[cls.__name__ for cls in self.__class__.__mro__]}")
        response = super().post(request, *args, **kwargs)
        print(f"   - Response status: {getattr(response, 'status_code', 'No status')}")
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
        print(f"🔎 _log_if_successful llamado:")
        print(f"   - action: {action}")
        print(f"   - response: {response}")
        print(f"   - response.status_code: {getattr(response, 'status_code', 'No status')}")
        
        if not self._is_successful_response(response, action):
            print(f"   - ❌ Response no es exitosa")
            return
        
        print(f"   - ✅ Response es exitosa, intentando logging")
        
        try:
            obj, obj_id = self._get_object_and_id(response, action, args, kwargs)
            if obj and obj_id:
                affected_value = self.log_config['get_value'](obj)
                
                print(f"   - 📝 Registrando log:")
                print(f"     - user: {request.user}")
                print(f"     - action: {action}")
                print(f"     - affected_type: {self.log_config['affected_type']}")
                print(f"     - affected_value: {affected_value}")
                print(f"     - affected_id: {obj_id}")
                
                log_user_action(
                    user=request.user,
                    action=action,
                    affected_type=self.log_config['affected_type'],
                    affected_value=affected_value,
                    affected_id=str(obj_id),
                    ip_address=get_client_ip(request)
                )
                print(f"   - ✅ Log registrado exitosamente")
            else:
                print(f"   - ❌ No se pudo obtener obj o obj_id")
        except Exception as e:
            print(f"   - ❌ Error en logging: {e}")
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
        
        print(f"🔍 Debug _get_object_and_id:")
        print(f"   - action: {action}")
        print(f"   - response type: {type(response)}")
        print(f"   - has data attr: {hasattr(response, 'data')}")
        print(f"   - args: {args}")
        print(f"   - kwargs: {kwargs}")
        
        if action == 'crear':
            # Para crear, intentar obtener el ID de la respuesta
            if hasattr(response, 'data') and isinstance(response.data, dict):
                obj_id = response.data.get('id')
                print(f"   - obj_id from response.data: {obj_id}")
                print(f"   - response.data: {response.data}")
            # Si no está en data, intentar con response directamente si es dict
            elif isinstance(response, dict):
                obj_id = response.get('id')
                print(f"   - obj_id from response dict: {obj_id}")
        else:
            # Para editar/eliminar, obtener ID de kwargs o args
            obj_id = kwargs.get('pk') or kwargs.get('user_id') or kwargs.get('obj_id')
            
            # Si no se encontró, buscar cualquier parámetro que termine en '_id'
            if not obj_id:
                for key, value in kwargs.items():
                    if key.endswith('_id') and value:
                        obj_id = value
                        print(f"   - Found ID in kwargs[{key}]: {obj_id}")
                        break
            
            # Como último recurso, intentar con args
            if not obj_id and args:
                obj_id = args[0] if args else None
            print(f"   - obj_id from kwargs/args: {obj_id}")
        
        print(f"   - final obj_id: {obj_id}, type: {type(obj_id)}")
        
        if obj_id and self.log_config['model_class']:
            try:
                obj = self.log_config['model_class'].objects.get(id=obj_id)
                print(f"   - ✅ Found object: {obj}")
                return obj, obj_id
            except Exception as e:
                print(f"   - ❌ Error getting object with ID {obj_id}: {e}")
                return None, None
        
        print(f"   - ⚠️ No valid obj_id or model_class")
        return None, None
