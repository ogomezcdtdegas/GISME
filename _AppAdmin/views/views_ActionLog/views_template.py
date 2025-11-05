"""
Vista template para mostrar la página de logs de acciones de usuarios
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from _AppAdmin.mixins import AdminPermissionMixin


class ActionLogTemplateView(LoginRequiredMixin, AdminPermissionMixin, TemplateView):
    """
    Vista para mostrar el template de logs de acciones de usuarios
    Solo accesible para admin y admin_principal
    """
    template_name = '_AppAdmin/actionlog/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'admin_actionlog'
        return context