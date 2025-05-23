from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from UTIL_LIB.propiedadesGas import calcular_propiedades_gas

'''------------------------ Controlador de redirección a template de fluxpro_propiedadesGas ---------------------'''
def FluxPro_view(request):
    return render(request, "_AppHerramientas/templates_fluxpro_propiedadesGas/index.html")
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