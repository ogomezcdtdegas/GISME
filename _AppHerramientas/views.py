from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pvtlib  

def FluxPro_view(request):
    return render(request, "_AppHerramientas/templates_fluxpro/index.html")


GASES_OPCIONES = {
    "C1": "Methane", "N2": "Nitrogen", "CO2": "Carbon Dioxide", "C2": "Ethane",
    "C3": "Propane", "iC4": "Isobutane", "nC4": "n-Butane", "iC5": "Isopentane",
    "nC5": "n-Pentane", "nC6": "Hexane", "nC7": "Heptane", "nC8": "Octane",
    "nC9": "Nonane", "nC10": "Decane", "H2": "Hydrogen", "O2": "Oxygen",
    "CO": "Carbon Monoxide", "H2O": "Water", "H2S": "Hydrogen Sulfide",
    "He": "Helium", "Ar": "Argon"
}

class FluxCalcProp_view(APIView):
    def get(self, request):
        """
        Si la solicitud es normal (no AJAX), renderiza la página.
        Si es AJAX, devuelve la configuración base.
        """
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX Request
            return Response({
                "message": "Bienvenido a FluxCalcProp",
                "gases": GASES_OPCIONES,
                "default_pressure": 1.0,
                "default_temperature": 40.0
            }, status=status.HTTP_200_OK)
        
        return render(request, "_AppHerramientas/templates_fluxpro/index.html", {"gases": GASES_OPCIONES})

    def post(self, request):
        """
        Recibe presión, temperatura y composición del gas para calcular propiedades.
        """
        try:
            P = float(request.data.get("pressure", 1.0))
            T = float(request.data.get("temperature", 40.0))

            composition = {}
            total_percentage = 0

            for gas_key, value in request.data.items():
                if gas_key.startswith("gas_"):
                    gas_id = gas_key.replace("gas_", "")
                    value = float(value)

                    if value > 0:
                        composition[gas_id] = value
                        total_percentage += value

            if total_percentage == 0:
                return Response({"error": "La composición del gas no puede ser 0%. Debe agregar al menos un gas."},
                                status=status.HTTP_400_BAD_REQUEST)

            gerg = pvtlib.AGA8("GERG-2008")
            gas_properties = gerg.calculate_from_PT(composition=composition, pressure=P, temperature=T)
            print(gas_properties)

            detail = pvtlib.AGA8("DETAIL")
            gas_properties_detail = detail.calculate_from_PT(composition=composition, pressure=P, temperature=T)

            return Response({
                "rho_gerg": f"{gas_properties['rho']:.3f} kg/m3",
                "rho_detail": f"{gas_properties_detail['rho']:.3f} kg/m3",
                "z_gerg": f"{gas_properties['z']:.3f}",
                "z_detail": f"{gas_properties_detail['z']:.3f}",
                "cp": f"{gas_properties_detail['cp']:.3f}",
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error en el cálculo: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
