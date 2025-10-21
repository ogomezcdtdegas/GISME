from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from _AppComplementos.models import Sistema
from _AppAuth.utils import get_monitoring_context

class MonitoreoCoriolisBaseView(LoginRequiredMixin, TemplateView):
    """Vista base SPA que renderiza el template principal con JavaScript"""
    template_name = '_AppMonitoreoCoriolis/coriolis_spa.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar contexto de permisos de monitoreo
        monitoring_context = get_monitoring_context(self.request.user)
        context.update(monitoring_context)
        
        context['active_section'] = 'monitoreo_coriolis'
        return context

class MonitoreoCoriolisSistemaView(LoginRequiredMixin, TemplateView):
    """Vista CBV para mostrar detalles específicos de un sistema"""
    template_name = '_AppMonitoreoCoriolis/coriolis_spa.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sistema = get_object_or_404(Sistema, id=kwargs['sistema_id'])
        
        # Agregar contexto de permisos de monitoreo
        monitoring_context = get_monitoring_context(self.request.user)
        context.update(monitoring_context)
        
        context.update({
            'sistema': sistema,
            'active_section': 'monitoreo_coriolis'
        })
        return context