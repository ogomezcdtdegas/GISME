from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from django.db.models import Q

from repoGenerico.views_base import BaseListView, BaseCreateView, BaseRetrieveUpdateView, BaseDeleteView
from .serializers import UserAdminSerializer
from .models import UserRole
from .mixins import AdminPermissionMixin
from _AppAuth.utils import get_admin_context


class AdminPanelView(LoginRequiredMixin, TemplateView):
    """Vista principal del panel de administración - Template View"""
    template_name = '_AppAdmin/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'admin'
        
        # Usar helper centralizado para obtener contexto de rol y permisos
        role_context = get_admin_context(self.request.user)
        context.update(role_context)
        
        # Configurar datos específicos según permisos
        if not context['access_denied'] and context['can_access_admin']:
            # Obtener usuarios con sus roles usando queryset directo
            usuarios = User.objects.select_related('user_role').all().order_by('-date_joined')
            context['usuarios'] = usuarios
            context['total_users'] = usuarios.count()
            
            # Roles disponibles
            context['available_roles'] = UserRole.ROLE_CHOICES
        else:
            context['usuarios'] = []
        
        return context


# API Views usando Repository Pattern + repoGenerico
class AdminUserListAPIView(AdminPermissionMixin, BaseListView):
    """API para listar usuarios - Extiende BaseListView del repoGenerico"""
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


class AdminUserCreateAPIView(AdminPermissionMixin, BaseCreateView):
    """API para crear usuarios - Extiende BaseCreateView del repoGenerico"""
    model = User
    serializer_class = UserAdminSerializer


class AdminUserDetailAPIView(AdminPermissionMixin, BaseRetrieveUpdateView):
    """API para obtener y actualizar usuarios - Extiende BaseRetrieveUpdateView del repoGenerico"""
    model = User
    serializer_class = UserAdminSerializer
    
    def get_queryset(self):
        """Override para incluir user_role en el queryset"""
        return User.objects.select_related('user_role').all()


class AdminUserDeleteAPIView(AdminPermissionMixin, BaseDeleteView):
    """API para eliminar usuarios - Extiende BaseDeleteView del repoGenerico"""
    model = User
    
    def delete(self, request, **kwargs):
        """Override para validaciones adicionales antes de eliminar"""
        try:
            # Obtener ID del usuario usando el método base
            obj_id = self._get_object_id_from_kwargs(kwargs)
            user_to_delete = self.model.objects.get(id=obj_id)
            
            # Validación: No permitir auto-eliminación
            if user_to_delete == request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'No puedes eliminarte a ti mismo'
                }, status=400)
            
            # Llamar al método base para realizar la eliminación
            return super().delete(request, **kwargs)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar usuario: {str(e)}'
            }, status=500)


class AdminRolesAPIView(AdminPermissionMixin, View):
    """API para obtener roles disponibles"""
    
    def get(self, request):
        try:
            roles = [
                {'value': choice[0], 'label': choice[1]} 
                for choice in UserRole.ROLE_CHOICES
            ]
            return JsonResponse({
                'success': True, 
                'roles': roles
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al obtener roles: {str(e)}'
            }, status=500)


# Mantener compatibilidad con URLs legacy si es necesario
class LegacyAdminView(AdminPanelView):
    """Vista de compatibilidad para URLs legacy"""
    pass
