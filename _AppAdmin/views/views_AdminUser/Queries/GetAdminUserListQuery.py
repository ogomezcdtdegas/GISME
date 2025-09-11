from django.contrib.auth.models import User
from repoGenerico.views_base import BaseListView
from ....serializers import UserAdminSerializer
from ....mixins import AdminPermissionMixin

class GetAdminUserListQuery(AdminPermissionMixin, BaseListView):
    """Query para listar usuarios administrativos - API JSON"""
    model = User
    serializer_class = UserAdminSerializer
    default_per_page = 10
    default_ordering = '-date_joined'
    
    def get_queryset(self):
        """Override para incluir user_role en el queryset"""
        return User.objects.select_related('user_role').all()
    
    def get_search_fields(self):
        """Campos permitidos para búsqueda"""
        return ['email', 'first_name', 'last_name', 'user_role__role']
    
    def get_allowed_ordering_fields(self):
        """Campos permitidos para ordenamiento"""
        return ['email', 'first_name', 'last_name', 'date_joined', 'user_role__role']
