from django.contrib.auth.models import User
from repoGenerico.views_base import BaseCreateView
from ....serializers import UserAdminCreateSerializer
from ....mixins import AdminPermissionMixin

class CreateAdminUserCommand(AdminPermissionMixin, BaseCreateView):
    """Command para crear usuarios administrativos"""
    model = User
    serializer_class = UserAdminCreateSerializer
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'admin'
        return context
