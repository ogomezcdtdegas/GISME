from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from repoGenerico.views_base import BaseRetrieveUpdateView
from ...models import Sistema
from ...serializers import SistemaSerializer
from _AppAuth.utils import get_user_role_context
from _AppAdmin.mixins import ComplementosPermissionMixin


class SistemasIndexView(ComplementosPermissionMixin, LoginRequiredMixin, TemplateView):
    """CBV Vista principal para gestión de sistemas"""
    template_name = '_AppComplementos/templates_sistema/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar contexto de permisos de usuario
        if hasattr(self.request, 'user'):
            context.update(get_user_role_context(self.request.user))
        
        context['active_section'] = 'complementos_sistema'
        return context


class SistemaBaseView(BaseRetrieveUpdateView):
    """Vista base para debugging de sistemas"""
    model = Sistema
    serializer_class = SistemaSerializer
    template_name = '_AppComplementos/templates_sistema/debug.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debug_info'] = f"Sistema ID: {self.kwargs.get('pk', 'N/A')}"
        return context
