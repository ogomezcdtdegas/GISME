from repoGenerico.views_base import BaseListView
from ....models import User
from ....serializers import UserAdminSerializer
from ....mixins import AdminPermissionMixin
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Q

# 🔹 API paginada (JSON)
@extend_schema_view(
    get=extend_schema(tags=['AdminUser'], description="Listado paginado de usuarios (API)")
)
class AdminUserPaginatedAPI(AdminPermissionMixin, BaseListView):
    model = User
    serializer_class = UserAdminSerializer
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')
    
    def get_allowed_ordering_fields(self):
        return ['date_joined', 'first_name', 'last_name', 'email']
    
    def apply_search_filters(self, queryset, search_query):
        """Aplicar filtros de búsqueda específicos para usuarios"""
        if search_query:
            return queryset.filter(
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        return queryset
