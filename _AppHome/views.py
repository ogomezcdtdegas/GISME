from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Equipo

# Create your views here.

''' -------------------------------------- '''
''' -------------- Querys ---------------- '''
''' -------------------------------------- '''

def allEquiposPag(request):
    equipos_list = Equipo.objects.all().order_by('-created_at')
    per_page = int(request.GET.get('per_page', 10))
    page_number = int(request.GET.get('page', 1))

    paginator = Paginator(equipos_list, per_page)
    equipos_page = paginator.get_page(page_number)

    # 🔹 Verifica si la solicitud es AJAX correctamente
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        equipos_data = [
            {
                "serial": equipo.serial,
                "sap": equipo.sap,
                "marca": equipo.marca,
                "created_at": equipo.created_at.strftime("%d-%m-%Y %H:%M")
            }
            for equipo in equipos_page
        ]

        return JsonResponse({
            "equipos": equipos_data,
            "has_previous": equipos_page.has_previous(),
            "has_next": equipos_page.has_next(),
            "previous_page_number": equipos_page.previous_page_number() if equipos_page.has_previous() else None,
            "next_page_number": equipos_page.next_page_number() if equipos_page.has_next() else None,
            "current_page": equipos_page.number,
            "total_pages": paginator.num_pages,
        }, safe=False)

    # 🔹 Si no es AJAX, renderiza el HTML
    return render(request, "_AppHome/index.html", {"equipos": equipos_page})




''' -------------------------------------- '''
''' -------------- Commands -------------- '''
''' -------------------------------------- '''
def crearEquipo(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        serial = request.POST.get("serial")
        sap = request.POST.get("sap")
        marca = request.POST.get("marca")

        if serial and sap and marca:
            equipo = Equipo.objects.create(serial=serial, sap=sap, marca=marca)
            return JsonResponse({
                "success": True,
                "equipo": {
                    "serial": equipo.serial,
                    "sap": equipo.sap,
                    "marca": equipo.marca,
                    "created_at": equipo.created_at.strftime("%d-%m-%Y %H:%M")
                }
            })

    return JsonResponse({"success": False, "error": "Datos inválidos"}, status=400)

        #return redirect("home")


