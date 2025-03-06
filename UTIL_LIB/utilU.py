
import metrolopy as uc

def calcular_incertidumbre(d,u_cal,u_res,u_der):
        # Obtener los valores de la solicitud JSON
        valor_medido_d = float(d)
        ucal = float(u_cal)  # ECalibración
        ures = float(u_res)  # resolución Instrumentos
        uder= float(u_der)  # deriva Instrumentos
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
        return({
            "valor_medido": APIv,
            "incertidumbre_expandida": uAPI,
            "histograma_data":APIdata
        })
