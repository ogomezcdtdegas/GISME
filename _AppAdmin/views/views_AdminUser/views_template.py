from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from _AppAuth.utils import get_admin_context
from _AppAdmin.mixins import AdminPermissionMixin

class AdminUserPaginatedHTML(LoginRequiredMixin, AdminPermissionMixin, TemplateView):
    """Vista principal para administración de usuarios - Solo renderiza template, datos via AJAX"""
    template_name = "_AppAdmin/index.html"

    def get_context_data(self, **kwargs):
        """Agregar contexto específico de administración"""
        context = super().get_context_data(**kwargs)
        
        # Usar helper centralizado para obtener contexto de rol y permisos
        role_context = get_admin_context(self.request.user)
        context.update(role_context)
        
        # Agregar información adicional para el template
        context.update({
            'active_section': 'admin',
            'page_title': 'Administración de Usuarios'
        })
        
        return context
