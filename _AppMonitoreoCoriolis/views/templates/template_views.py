from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from _AppComplementos.models import Sistema
from _AppAuth.utils import get_monitoring_context
from _AppMonitoreoCoriolis.models import BatchDetectado
from django.db.models import Sum
from datetime import datetime, timedelta
import pytz

# Zona horaria de Colombia
COLOMBIA_TZ = pytz.timezone('America/Bogota')

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
        
        # Calcular masa de cierre del día anterior
        masa_dia_anterior = self._calcular_masa_dia_anterior(sistema.id)
        
        # Obtener fecha del día anterior formateada
        ahora = datetime.now(COLOMBIA_TZ)
        fecha_dia_anterior = (ahora - timedelta(days=1)).strftime('%d/%m/%Y')
        
        context.update({
            'sistema': sistema,
            'active_section': 'monitoreo_coriolis',
            'masa_dia_anterior': masa_dia_anterior,
            'fecha_dia_anterior': fecha_dia_anterior
        })
        return context
    
    def _calcular_masa_dia_anterior(self, sistema_id):
        """
        Calcula la suma de mass_total de todos los batches del día anterior
        para el sistema especificado.
        
        Returns:
            float: Suma total de masa en kg del día anterior, o 0.0 si no hay batches
        """
        # Obtener fecha actual en zona horaria de Colombia
        ahora = datetime.now(COLOMBIA_TZ)
        
        # Calcular inicio y fin del día anterior
        inicio_dia_anterior = (ahora - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia_anterior = (ahora - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Consultar batches del día anterior para este sistema
        resultado = BatchDetectado.objects.filter(
            systemId_id=sistema_id,
            fecha_inicio__gte=inicio_dia_anterior,
            fecha_inicio__lte=fin_dia_anterior
        ).aggregate(total_masa=Sum('mass_total'))
        
        # Retornar el total redondeado a 2 decimales o 0 si no hay batches
        return round(resultado['total_masa'], 2) if resultado['total_masa'] is not None else 0.0