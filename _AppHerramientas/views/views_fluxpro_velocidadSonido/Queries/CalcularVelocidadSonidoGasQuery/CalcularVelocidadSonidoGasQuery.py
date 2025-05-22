from django.shortcuts import render

def FluxProVel_view(request):
    return render(request, "_AppHerramientas/templates_fluxpro_velocidadSonido/index.html")