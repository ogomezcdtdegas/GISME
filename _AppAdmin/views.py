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


class AdminPanelView(LoginRequiredMixin, TemplateView):
    """Vista principal del panel de administración - Template View"""
    template_name = '_AppAdmin/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'admin'
        
        # Obtener rol del usuario actual
        user_role = None
        if hasattr(self.request.user, 'user_role'):
            user_role = self.request.user.user_role.role
        
        context['current_user_role'] = user_role
        
        # Configurar permisos y datos según rol
        if user_role == 'supervisor':
            context['access_denied'] = True
            context['access_denied_message'] = 'Su tipo de usuario Supervisor no tiene permiso de acceso. Solo Administradores.'
            context['usuarios'] = []
        elif user_role in ['admin', 'admin_principal']:
            context['access_denied'] = False
            # Obtener usuarios con sus roles usando queryset directo
            usuarios = User.objects.select_related('user_role').all().order_by('-date_joined')
            context['usuarios'] = usuarios
            context['total_users'] = usuarios.count()
            
            # Permisos específicos por rol
            context['can_access_admin'] = True
            context['can_create_users'] = user_role == 'admin_principal'
            context['can_edit_users'] = user_role == 'admin_principal'
            context['can_delete_users'] = user_role == 'admin_principal'
            
            # Roles disponibles
            context['available_roles'] = UserRole.ROLE_CHOICES
        else:
            context['access_denied'] = True
            context['access_denied_message'] = 'Su rol de usuario no tiene permisos para acceder al módulo de administración de usuarios.'
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
