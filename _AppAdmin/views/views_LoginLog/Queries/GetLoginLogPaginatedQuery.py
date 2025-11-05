"""
API para logs de login de usuarios con paginación y filtro por email
Sigue el patrón de criticidad para consistencia
"""
from repoGenerico.views_base import BaseListView
from django.db.models import Q
from _AppAuth.models import UserLoginLog
from _AppAdmin.serializers import UserLoginLogSerializer
from _AppAdmin.mixins import AdminPermissionMixin
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    get=extend_schema(tags=['LoginLog'], description="Listado paginado de logs de login (API)")
)
class GetLoginLogPaginatedQuery(AdminPermissionMixin, BaseListView):
    """
    API para obtener logs de login paginados con filtro por email
    Solo usuarios admin y admin_principal pueden acceder
    """
    model = UserLoginLog
    serializer_class = UserLoginLogSerializer
    default_ordering = '-login_datetime'
    
    def get_queryset(self):
        return UserLoginLog.objects.all().order_by('-login_datetime')
    
    def get_allowed_ordering_fields(self):
        return ['login_datetime', 'email', 'created_at']
    
    def apply_search_filters(self, queryset, search_query):
        """Aplicar filtros de búsqueda específicos para logs de login"""
        if search_query:
            return queryset.filter(
                Q(email__icontains=search_query) |
                Q(ip_address__icontains=search_query)
            )
        return queryset