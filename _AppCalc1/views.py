from django.shortcuts import render
from django.http import JsonResponse
import pvtlib  # Asegúrate de que esta librería esté instalada

GASES_OPCIONES = {
    "C1": "Methane",
    "N2": "Nitrogen",
    "CO2": "Carbon Dioxide",
    "C2": "Ethane",
    "C3": "Propane",
    "iC4": "Isobutane",
    "nC4": "n-Butane",
    "iC5": "Isopentane",
    "nC5": "n-Pentane",
    "nC6": "Hexane",
    "nC7": "Heptane",
    "nC8": "Octane",
    "nC9": "Nonane",
    "nC10": "Decane",
    "H2": "Hydrogen",
    "O2": "Oxygen",
    "CO": "Carbon Monoxide",
    "H2O": "Water",
    "H2S": "Hydrogen Sulfide",
    "He": "Helium",
    "Ar": "Argon",
}

def calc1_view(request):

    context = {"gases": GASES_OPCIONES}  # Pasar los gases al template

    if request.method == "POST":
        try:
            # Obtener Presión y Temperatura
            P = float(request.POST.get("pressure", 1.0))
            T = float(request.POST.get("temperature", 40.0))

            # Construir el diccionario de composición
            composition = {}
            total_percentage = 0

            for key in request.POST:
                if key.startswith("gas_"):
                    gas_key = key.replace("gas_", "")
                    value = float(request.POST[key])

                    if value > 0:
                        composition[gas_key] = value
                        total_percentage += value

            # Verificar si la composición es válida
            if total_percentage == 0:
                context["error"] = "La composición del gas no puede ser 0%. Debe agregar al menos un gas."
                return render(request, "AppCalc1/index.html", context)

            # Calcular propiedades con GERG-2008
            gerg = pvtlib.AGA8("GERG-2008")
            gas_properties = gerg.calculate_from_PT(composition=composition, pressure=P, temperature=T)

            # Calcular propiedades con DETAIL
            detail = pvtlib.AGA8("DETAIL")
            gas_properties_detail = detail.calculate_from_PT(composition=composition, pressure=P, temperature=T)

            context["results"] = {
                "rho_gerg": f"{gas_properties['rho']:.3f} kg/m3",
                "rho_detail": f"{gas_properties_detail['rho']:.3f} kg/m3",
                "z_gerg": f"{gas_properties['z']:.3f}",
                "z_detail": f"{gas_properties_detail['z']:.3f}",
            }

        except Exception as e:
            context["error"] = "La composición del gas no puede ser 0%. Debe agregar al menos un gas."
    # Puedes elegir la plantilla dinámicamente
    template = request.GET.get('template', '_AppCalc1/index.html')  
    return render(request, template, context)

