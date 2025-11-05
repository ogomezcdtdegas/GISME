"""
Vistas para Usuario con logging automático de acciones
"""
from django.contrib.auth import get_user_model
from _AppAdmin.mixins import UniversalActionLogMixin
from .Commands.CreateAdminUserCommand import CreateAdminUserCommand
from .Commands.UpdateAdminUserCommand import UpdateAdminUserCommand
from .Commands.DeleteAdminUserCommand import DeleteAdminUserCommand

User = get_user_model()


class CreateAdminUserWithLogging(UniversalActionLogMixin, CreateAdminUserCommand):
    log_config = {
        'affected_type': 'usuario',
        'get_value': lambda obj: obj.email,
        'model_class': User,
    }
    
    def post(self, request, *args, **kwargs):
        print(f"🎯 CreateAdminUserWithLogging.post() ejecutándose")
        print(f"   - self.__class__: {self.__class__}")
        print(f"   - MRO: {[cls.__name__ for cls in self.__class__.__mro__]}")
        print(f"   - log_config: {self.log_config}")
        
        # Llamar al método padre
        result = super().post(request, *args, **kwargs)
        print(f"   - Resultado del super().post(): {result}")
        print(f"   - Status code: {getattr(result, 'status_code', 'No status')}")
        
        return result


class UpdateAdminUserWithLogging(UniversalActionLogMixin, UpdateAdminUserCommand):
    log_config = {
        'affected_type': 'usuario',
        'get_value': lambda obj: obj.email,
        'model_class': User,
    }


class DeleteAdminUserWithLogging(UniversalActionLogMixin, DeleteAdminUserCommand):
    log_config = {
        'affected_type': 'usuario',
        'get_value': lambda obj: obj.email,
        'model_class': User,
    }