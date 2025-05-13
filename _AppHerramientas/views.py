from django.shortcuts import render

def FluxPro_view(request):
    return render(request, "_AppHerramientas/templates_fluxpro/index.html")
