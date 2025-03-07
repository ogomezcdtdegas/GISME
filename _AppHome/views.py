from django.shortcuts import render
from .models import Equipo 
# Create your views here.

def index(request):
    return render(request, '_AppHome/index.html')

def gestion_equipos(request):
    if request.method == "POST":
        serial = request.POST.get("serial")
        sap = request.POST.get("sap")
        marca = request.POST.get("marca")

        if serial and sap and marca:
            Equipo.objects.create(serial=serial, sap=sap, marca=marca)

    equipos = Equipo.objects.all().order_by('-created_at')  # Ordenar por fecha descendente
    return render(request, "_AppHome/index.html", {"equipos": equipos})
