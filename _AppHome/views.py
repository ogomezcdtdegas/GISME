from django.shortcuts import render, redirect
from .models import Equipo
from django.core.paginator import Paginator

# Create your views here.

''' -------------------------------------- '''
''' -------------- Querys -------------- '''
''' -------------------------------------- '''
def index(request):
    equipos_list = Equipo.objects.all().order_by('-created_at')  # Orden descendente
    per_page = request.GET.get('per_page', 10)  # Registros por página, por defecto 10
    page_number = request.GET.get('page', 1)  # Número de página

    paginator = Paginator(equipos_list, per_page)
    equipos = paginator.get_page(page_number)

    return render(request, "_AppHome/index.html", {"equipos": equipos})
    #return render(request, '_AppHome/index.html')



''' -------------------------------------- '''
''' -------------- Commands -------------- '''
''' -------------------------------------- '''
def crearEquipo(request):
    if request.method == "POST":
        serial = request.POST.get("serial")
        sap = request.POST.get("sap")
        marca = request.POST.get("marca")

        if serial and sap and marca:
            Equipo.objects.create(serial=serial, sap=sap, marca=marca)

        return redirect("home")


