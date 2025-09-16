from django.contrib.auth.models import User
from repoGenerico.views_base import BaseCreateView
from ....serializers import UserAdminCreateSerializer
from ....mixins import AdminPermissionMixin

class CreateAdminUserCommand(AdminPermissionMixin, BaseCreateView):
    """Command para crear usuarios administrativos"""
    model = User
    serializer_class = UserAdminCreateSerializer
    
    def post(self, request, *args, **kwargs):
        print(f"⚡ CreateAdminUserCommand.post() ejecutándose")
        print(f"   - self.__class__: {self.__class__}")
        print(f"   - request.path: {request.path}")
        print(f"   - request.method: {request.method}")
        return super().post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'admin'
        return context
