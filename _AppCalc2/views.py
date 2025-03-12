from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import metrolopy as uc
from django.utils.timezone import now

class IncertidumbreAPIView(APIView):

    def get(self, request):
        """Renderiza la página con el timestamp."""
        return render(request, '_AppCalc2/index.html', {'timestamp': now().timestamp()})

    def post(self, request):
        """Calcula la incertidumbre y devuelve los resultados."""
        print("✅ Recibida solicitud POST a /calc2/incertidumbre/")

        try:
            data = request.data
            print("📌 Datos recibidos:", data)

            if not all(k in data for k in ['densidad_medida', 'u_cal', 'u_res', 'u_der']):
                return Response({"error": "Faltan datos en la solicitud"}, status=400)

            # Convertir a float y validar
            valor_medido_d = float(data.get('densidad_medida', 0))
            ucal = float(data.get('u_cal', 0))
            ures = float(data.get('u_res', 0))
            uder = float(data.get('u_der', 0))

            if valor_medido_d < 0 or ucal < 0 or ures < 0 or uder < 0:
                return Response({"error": "Los valores deben ser positivos"}, status=400)

            # Cálculo de incertidumbre
            k = 2
            ucal_mp = uc.gummy(0, u=ucal/k)
            ures_mp = uc.gummy(uc.UniformDist(center=0.0, half_width=ures/2))
            uder_mp = uc.gummy(uc.UniformDist(center=0.0, half_width=uder/2))

            API = valor_medido_d + ucal_mp + ures_mp + uder_mp
            API.p = 0.95
            API.sim()
            uAPI = (API.Usim[0] + API.Usim[0]) / 2
            APIv = API.xsim
            APId = API.simdata
            APIdata = APId.tolist()

            print("✅ Cálculo exitoso.")

            return Response({
                "valor_medido": APIv,
                "incertidumbre_expandida": uAPI,
                "histograma_data": APIdata
            })

        except Exception as e:
            print("❌ Error en el cálculo:", e)
            return Response({"error": f"Error en los cálculos: {str(e)}"}, status=400)
