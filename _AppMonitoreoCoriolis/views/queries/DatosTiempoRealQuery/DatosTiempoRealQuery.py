import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema
from _AppMonitoreoCoriolis.models import NodeRedData
from UTIL_LIB.conversiones import celsius_a_fahrenheit, cm3_s_a_gal_min, lb_s_a_kg_min, cm3_a_gal, lb_a_kg
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ, get_coeficientes_correccion, convertir_presion_con_span

# Configurar logging
logger = logging.getLogger(__name__)

class DatosTiempoRealQueryView(APIView):
    """
    CBV para obtener los últimos datos para mostrar en los displays en tiempo real
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sistema_id):
        try:
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener coeficientes de corrección
            mt, bt, mp, bp, span_presion, zero_presion = get_coeficientes_correccion(sistema)
            
            # Obtener el último registro
            ultimo_dato = NodeRedData.objects.filter(
                systemId=sistema
            ).order_by('-created_at').first()
            
            if not ultimo_dato:
                return Response({
                    'success': False,
                    'error': 'No hay datos disponibles para este sistema'
                }, status=404)
            
            # Convertir UTC a hora de Colombia
            fecha_colombia = ultimo_dato.created_at.astimezone(COLOMBIA_TZ)
            
            # Aplicar corrección a Temperatura de Salida (redundant_temperature)
            temp_salida = ultimo_dato.redundant_temperature
            temp_salida_corr = mt * float(temp_salida) + bt if temp_salida is not None else None
            
            # Aplicar corrección a Presión (pressure_out)
            presion = ultimo_dato.pressure_out
            if presion is not None:
                # 1. Convertir valor crudo con span
                valor_convertido = convertir_presion_con_span(presion, span_presion)
                # 2. Aplicar corrección mx+b
                presion_corr = mp * valor_convertido + bp
            else:
                presion_corr = None
            
            return Response({
                'success': True,
                'datos': {
                    'flujo': {
                        'valor': cm3_s_a_gal_min(ultimo_dato.flow_rate),
                        'unidad': 'gal/min'
                    },
                    'flujoMasico': {
                        'valor': lb_s_a_kg_min(ultimo_dato.mass_rate),
                        'unidad': 'kg/min'
                    },
                    'temperaturaRedundante': {
                        'valor': celsius_a_fahrenheit(temp_salida_corr) if temp_salida_corr is not None else None,
                        'unidad': '°F'
                    },
                    'temperaturaDiagnostico': {
                        'valor': celsius_a_fahrenheit(ultimo_dato.diagnostic_temperature),
                        'unidad': '°F'
                    },
                    'temperatura': {
                        'valor': celsius_a_fahrenheit(ultimo_dato.coriolis_temperature),
                        'unidad': '°F'
                    },
                    'presion': {
                        'valor': float(presion_corr) if presion_corr is not None else 0,
                        'unidad': 'PSI'
                    },
                    'volTotal': {
                        'valor': cm3_a_gal(ultimo_dato.total_volume),
                        'unidad': 'gal'
                    },
                    'masTotal': {
                        'valor': lb_a_kg(ultimo_dato.total_mass),
                        'unidad': 'kg'
                    },
                    'densidad': {
                        'valor': float(ultimo_dato.density) if ultimo_dato.density else 0,
                        'unidad': 'g/cc'
                    },
                    'frecuencia': {
                        'valor': float(ultimo_dato.coriolis_frecuency) if ultimo_dato.coriolis_frecuency else 0,
                        'unidad': 'Hz'
                    },
                    'concSolido': {
                        'valor': float(ultimo_dato.pconc) if ultimo_dato.pconc else 0,
                        'unidad': '%'
                    },
                    'corteAgua': {
                        'valor': float(ultimo_dato.percent_cutWater64b) if ultimo_dato.percent_cutWater64b else 0,
                        'unidad': '%'
                    },
                    'signalGateway': {
                        'valor': float(ultimo_dato.signal_strength_rxCoriolis) if ultimo_dato.signal_strength_rxCoriolis else 0,
                        'unidad': 'dB'
                    },
                    'tempGateway': {
                        'valor': float(ultimo_dato.temperature_gateway) if ultimo_dato.temperature_gateway else 0,
                        'unidad': '°C'  # Esta se mantiene en °C según lo solicitado
                    }
                },
                'timestamp': fecha_colombia.isoformat(),
                'fecha_legible': fecha_colombia.strftime('%d/%m/%Y %H:%M:%S')
            })
            
        except Sistema.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Sistema no encontrado'
            }, status=404)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)