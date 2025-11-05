from django.contrib.auth.models import User
from repoGenerico.views_base import BaseRetrieveUpdateView
from ....serializers import UserAdminUpdateSerializer
from ....mixins import AdminPermissionMixin

class UpdateAdminUserCommand(AdminPermissionMixin, BaseRetrieveUpdateView):
    """Command para obtener y actualizar usuarios administrativos"""
    model = User
    serializer_class = UserAdminUpdateSerializer
    
    def get_queryset(self):
        """Override para incluir user_role en el queryset"""
        return User.objects.select_related('user_role').all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'admin'
        return context
    
    def get(self, request, *args, **kwargs):
        """Manejar GET - obtener datos del usuario"""
        return super().get(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        """Manejar PUT - actualizar usuario"""
        return super().put(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        """Manejar PATCH - actualización parcial"""
        return super().patch(request, *args, **kwargs)
