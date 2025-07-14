from django.shortcuts import render, get_object_or_404
from _AppComplementos.models import Sistema

def monitoreo_coriolis_index(request):
    """Vista principal de Monitoreo Coriolis - Muestra tabla de selección de sistemas"""
    context = {
        'active_section': 'monitoreo_coriolis',
        'show_selector': True  # Flag para mostrar tabla de selección
    }
    return render(request, '_AppMonitoreoCoriolis/coriolis_hybrid.html', context)

def monitoreo_coriolis_sistema(request, sistema_id):
    """Vista de Monitoreo Coriolis para un sistema específico"""
    sistema = get_object_or_404(Sistema, id=sistema_id)
    
    context = {
        'active_section': 'monitoreo_coriolis',
        'sistema': sistema,
        'show_selector': False  # Flag para mostrar dashboard de monitoreo
    }
    return render(request, '_AppMonitoreoCoriolis/coriolis_hybrid.html', context)
