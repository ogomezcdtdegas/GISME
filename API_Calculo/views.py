from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import metrolopy as uc
def home(request):
    return render(request, "Templates/index.html")


def calcular_incertidumbre(request):
    try:
        # Obtener los valores de la solicitud JSON
        valor_medido_d = float(request.data.get('densidad_medida'))
        ucal = float(request.data.get('u_cal'))  # ECalibración
        ures = float(request.data.get('u_res'))  # resolución Instrumentos
        uder= float(request.data.get('u_der'))  # deriva Instrumentos
        k=2

        # Crear la medición con MetrologyPy
        ucal_mp=uc.gummy(0,u=ucal/k)
        ures_mp=uc.gummy(uc.UniformDist(center=0.0,half_width=ures/2))
        uder_mp=uc.gummy(uc.UniformDist(center=0.0,half_width=uder/2))
        
        API=valor_medido_d+ucal_mp+ures_mp+uder_mp
        
        #Simular modelo montecarlo
        #plt.ion()
        API.p=0.95
        API.sim()
        uAPI=(API.Usim[0]+API.Usim[0])/2
        APIv=API.xsim
        APId=API.simdata
        APIdata=APId.tolist()

        # Respuesta en formato JSON
        return Response({
            "valor_medido": APIv,
            "incertidumbre_expandida": uAPI,
            "histograma_data":APIdata
        })

    except (TypeError, ValueError):
        return Response({"error": "Datos inválidos"}, status=400)
