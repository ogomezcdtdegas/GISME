"""
API para logs de login de usuarios con paginación y filtro por email
Sigue el patrón de criticidad para consistencia
"""
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from _AppAuth.models import UserLoginLog
from _AppAdmin.serializers import UserLoginLogSerializer
from _AppAdmin.mixins import AdminPermissionMixin


class LoginLogPagination(PageNumberPagination):
    """
    Paginación personalizada para logs de login
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class GetLoginLogPaginatedQuery(AdminPermissionMixin, ListAPIView):
    """
    API para obtener logs de login paginados con filtro por email
    Solo usuarios admin y admin_principal pueden acceder
    """
    serializer_class = UserLoginLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LoginLogPagination
    
    def get_queryset(self):
        """
        Obtener queryset de logs con filtro opcional por email
        """
        queryset = UserLoginLog.objects.all().order_by('-login_datetime')
        
        # Filtro por email si se proporciona
        email = self.request.query_params.get('email', None)
        if email:
            queryset = queryset.filter(email__icontains=email)
        
        return queryset