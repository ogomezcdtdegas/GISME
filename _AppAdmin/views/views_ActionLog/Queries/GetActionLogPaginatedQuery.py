"""
API para logs de acciones de usuarios con paginación y filtros
Sigue el patrón de criticidad para consistencia
"""
from repoGenerico.views_base import BaseListView
from django.db.models import Q
from _AppAdmin.models import UserActionLog
from _AppAdmin.serializers import UserActionLogSerializer
from _AppAdmin.mixins import AdminPermissionMixin
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    get=extend_schema(tags=['ActionLog'], description="Listado paginado de logs de acciones (API)")
)
class GetActionLogPaginatedQuery(AdminPermissionMixin, BaseListView):
    """
    API para obtener logs de acciones paginados con filtros
    Solo usuarios admin y admin_principal pueden acceder
    """
    model = UserActionLog
    serializer_class = UserActionLogSerializer
    default_ordering = '-action_datetime'
    
    def get_queryset(self):
        queryset = UserActionLog.objects.all().order_by('-action_datetime')
        
        # Aplicar filtros específicos si están presentes
        request = getattr(self, 'request', None)
        if request:
            # Filtro por acción específica
            action_filter = request.GET.get('action', '').strip()
            if action_filter:
                queryset = queryset.filter(action__icontains=action_filter)
            
            # Filtro por tipo afectado específico
            affected_type_filter = request.GET.get('affected_type', '').strip()
            if affected_type_filter:
                queryset = queryset.filter(affected_type__icontains=affected_type_filter)
            
            # Filtro por email específico
            email_filter = request.GET.get('email', '').strip()
            if email_filter:
                queryset = queryset.filter(email__icontains=email_filter)
        
        return queryset
    
    def get_allowed_ordering_fields(self):
        return ['action_datetime', 'email', 'action', 'affected_type', 'created_at']
    
    def apply_search_filters(self, queryset, search_query):
        """Aplicar filtros de búsqueda específicos para logs de acciones"""
        if search_query:
            return queryset.filter(
                Q(email__icontains=search_query) |
                Q(action__icontains=search_query) |
                Q(affected_type__icontains=search_query) |
                Q(affected_value__icontains=search_query)
            )
        return queryset