"""
API para logs de acciones de usuarios con paginación y filtros
Sigue el patrón de criticidad para consistencia
"""
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from _AppAdmin.models import UserActionLog
from _AppAdmin.serializers import UserActionLogSerializer
from _AppAdmin.mixins import AdminPermissionMixin


class ActionLogPagination(PageNumberPagination):
    """
    Paginación personalizada para logs de acciones
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class GetActionLogPaginatedQuery(AdminPermissionMixin, ListAPIView):
    """
    API para obtener logs de acciones paginados con filtros
    Solo usuarios admin y admin_principal pueden acceder
    """
    serializer_class = UserActionLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ActionLogPagination
    
    def get_queryset(self):
        """
        Obtener queryset de logs con filtros opcionales
        """
        queryset = UserActionLog.objects.all().order_by('-action_datetime')
        
        # Filtro por email si se proporciona
        email = self.request.query_params.get('email', None)
        if email:
            queryset = queryset.filter(email__icontains=email)
        
        # Filtro por acción si se proporciona
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)
        
        # Filtro por tipo afectado si se proporciona
        affected_type = self.request.query_params.get('affected_type', None)
        if affected_type:
            queryset = queryset.filter(affected_type=affected_type)
        
        # Filtro por valor afectado si se proporciona
        affected_value = self.request.query_params.get('affected_value', None)
        if affected_value:
            queryset = queryset.filter(affected_value__icontains=affected_value)
        
        return queryset