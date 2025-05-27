from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from UTIL_LIB.propiedadesGas import calcular_propiedades_gas

GASES = [
    {"label": "Metano", "id": "gas_C1", "name": "gas_C1"},
    {"label": "Nitrógeno", "id": "gas_N2", "name": "gas_N2"},
    {"label": "Dióxido de Carbono", "id": "gas_CO2", "name": "gas_CO2"},
    {"label": "Etano", "id": "gas_C2", "name": "gas_C2"},
    {"label": "Propano", "id": "gas_C3", "name": "gas_C3"},
    {"label": "Agua", "id": "gas_H2O", "name": "gas_H2O"},
    {"label": "Sulfuro de Hidrógeno", "id": "gas_H2S", "name": "gas_H2S"},
    {"label": "Hidrógeno", "id": "gas_H2", "name": "gas_H2"},
    {"label": "Monóxido de Carbono", "id": "gas_CO", "name": "gas_CO"},
    {"label": "Oxígeno", "id": "gas_O2", "name": "gas_O2"},
    {"label": "i-Butano", "id": "gas_iC4", "name": "gas_iC4"},
    {"label": "n-Butano", "id": "gas_nC4", "name": "gas_nC4"},
    {"label": "i-Pentano", "id": "gas_iC5", "name": "gas_iC5"},
    {"label": "n-Pentano", "id": "gas_nC5", "name": "gas_nC5"},
    {"label": "n-Hexano", "id": "gas_nC6", "name": "gas_nC6"},
    {"label": "n-Heptano", "id": "gas_nC7", "name": "gas_nC7"},
    {"label": "n-Octano", "id": "gas_nC8", "name": "gas_nC8"},
    {"label": "n-Nonano", "id": "gas_nC9", "name": "gas_nC9"},
    {"label": "n-Decano", "id": "gas_nC10", "name": "gas_nC10"},
    {"label": "Helio", "id": "gas_He", "name": "gas_He"},
    {"label": "Argón", "id": "gas_Ar", "name": "gas_Ar"},
]

RESULTADOS_IZQ = [
    {"label": "Zf", "id": "Zf", "title": "Factor de Compresibilidad a condiciones de flujo", "unidad": "_"},
    {"label": "Zb", "id": "Zb", "title": "Factor de Compresibilidad a condiciones de base", "unidad": "_"},
    {"label": "ρ", "id": "ρ", "title": "Densidad Absoluta", "unidad": "lb/ft³"},
    {"label": "Hv", "id": "Hv", "title": "Poder Calorífico Superior ajustado a condiciones base", "unidad": "Btu/ft³"},
    {"label": "μ", "id": "μ", "title": "Viscosidad", "unidad": "Cp"},
]

RESULTADOS_DER = [
    {"label": "Gr", "id": "gr", "title": "Densidad Relativa", "unidad": "_"},
    {"label": "lw", "id": "lw", "title": "Indice de Wobbe", "unidad": "Btu/ft³"},
    {"label": "Mr", "id": "mm", "title": "Masa Molar", "unidad": "g/mol"},
    {"label": "dx", "id": "dx", "title": "Densidad Molar", "unidad": "mol/l"},
]

'''------------------------ Controlador de redirección a template de fluxpro_propiedadesGas ---------------------'''
def FluxPro_view(request):
    return render(request, "_AppHerramientas/templates_fluxpro_propiedadesGas/index.html", {"gases": GASES, "resultados_izq": RESULTADOS_IZQ, "resultados_der": RESULTADOS_DER})
''' ------------------------------------------------------------------------------------------------------------- '''

'''------------------------ Controlador para calculo de propiedades de gas --------------------------------------'''
class FluxCalcProp_view(APIView):
    def post(self, request):
        try:
            resultado = calcular_propiedades_gas(request.data)
            if "error" in resultado:
                return Response({"error": resultado["error"]}, status=status.HTTP_400_BAD_REQUEST)
            return Response(resultado, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error en el cálculo: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
''' ------------------------------------------------------------------------------------------------------------- '''