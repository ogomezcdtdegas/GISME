from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def sistemas_index(request):
    """Vista principal para gestión de sistemas"""
    context = {
        'active_section': 'complementos_sistema'
    }
    return render(request, '_AppComplementos/templates_sistema/index.html', context)
