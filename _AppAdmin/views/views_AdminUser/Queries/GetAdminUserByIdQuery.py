from django.contrib.auth.models import User
from repoGenerico.views_base import BaseRetrieveView
from ....serializers import UserAdminSerializer
from ....mixins import AdminPermissionMixin

class GetAdminUserByIdQuery(AdminPermissionMixin, BaseRetrieveView):
    """Query para obtener un usuario específico por ID"""
    model = User
    serializer_class = UserAdminSerializer
    
    def get_queryset(self):
        """Override para incluir user_role en el queryset"""
        return User.objects.select_related('user_role').all()
