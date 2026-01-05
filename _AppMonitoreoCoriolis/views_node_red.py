from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import NodeRedData
from .serializers import NodeRedDataSerializer
from repoGenerico.views_base import BasicNodeRedAuthMixin, BaseCreateView
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes
from UTIL_LIB.conversiones import (
    celsius_a_fahrenheit, cm3_s_a_gal_min, lb_s_a_kg_min,
    cm3_a_gal, lb_a_kg
)
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class NodeRedReceiverView(BasicNodeRedAuthMixin, BaseCreateView):
    model = NodeRedData
    serializer_class = NodeRedDataSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        auth_error = self.check_basic_auth(request)
        if auth_error:
            return auth_error

        mac_gateway = request.data.get("mac_gateway")
        sistema = Sistema.objects.filter(sistema_id=mac_gateway).first()
        if not mac_gateway or not sistema:
            return Response(
                {"detail": "mac_gateway no registrado como sistema_id en sistemas."},
                status=400
            )

        # Copia los datos y agrega el systemId
        data = request.data.copy()
        data['systemId'] = str(sistema.id)  # UUID a string

        # Obtener coeficientes de corrección vigentes al momento del registro
        try:
            coef = ConfiguracionCoeficientes.objects.get(systemId=sistema)
            data['mt'] = coef.mt
            data['bt'] = coef.bt
            data['mp'] = coef.mp
            data['bp'] = coef.bp
            data['vol_detect_batch'] = coef.vol_masico_ini_batch
            data['time_closed_batch'] = coef.time_finished_batch
        except ConfiguracionCoeficientes.DoesNotExist:
            # Valores por defecto si no hay coeficientes configurados
            data['mt'] = 1.0
            data['bt'] = 0.0
            data['mp'] = 1.0
            data['bp'] = 0.0
            data['vol_detect_batch'] = 75.0 # Valor por defecto kg
            data['time_closed_batch'] = 5   # Valor por defecto min

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            
            # 🚀 NUEVO: Notificar a clientes WebSocket conectados
            try:
                channel_layer = get_channel_layer()
                room_group_name = f'tendencias_{sistema.id}'
                
                # Obtener coeficientes de corrección para aplicar
                try:
                    coef = ConfiguracionCoeficientes.objects.get(systemId=sistema)
                    mt = coef.mt
                    bt = coef.bt
                    mp = coef.mp
                    bp = coef.bp
                except ConfiguracionCoeficientes.DoesNotExist:
                    mt = 1.0
                    bt = 0.0
                    mp = 1.0
                    bp = 0.0
                
                # Aplicar correcciones
                temp_salida = celsius_a_fahrenheit(obj.redundant_temperature) if obj.redundant_temperature else None
                temp_salida_corr = mt * float(temp_salida) + bt if temp_salida is not None else None
                
                presion_corr = mp * float(obj.pressure_out) + bp if obj.pressure_out else None
                
                # Preparar TODOS los datos para enviar (tendencias + tiempo real)
                datos_websocket = {
                    # Datos para gráfico de tendencias
                    'flujo_masico': lb_s_a_kg_min(float(obj.mass_rate)) if obj.mass_rate else None,
                    'flujo_volumetrico': cm3_s_a_gal_min(float(obj.flow_rate)) if obj.flow_rate else None,
                    'temperatura_coriolis': celsius_a_fahrenheit(float(obj.coriolis_temperature)) if obj.coriolis_temperature else None,
                    'temperatura_salida': temp_salida_corr,
                    'presion': presion_corr,
                    'densidad': float(obj.density) if obj.density else None,
                    
                    # Datos adicionales para displays en tiempo real
                    'temperatura_diagnostico': celsius_a_fahrenheit(float(obj.diagnostic_temperature)) if obj.diagnostic_temperature else None,
                    'vol_total': cm3_a_gal(obj.total_volume) if obj.total_volume else None,
                    'mas_total': lb_a_kg(obj.total_mass) if obj.total_mass else None,
                    'frecuencia': float(obj.coriolis_frecuency) if obj.coriolis_frecuency else None,
                    'noise_n1': float(obj.dsp_rxmsg_noiseEstimatedN1) if obj.dsp_rxmsg_noiseEstimatedN1 else None,
                    'noise_n2': float(obj.dsp_rxmsg_noiseEstimatedN2) if obj.dsp_rxmsg_noiseEstimatedN2 else None,
                    'driver_amplitude': float(obj.dsp_rxmsg_driverAmplitude) if obj.dsp_rxmsg_driverAmplitude else None,
                    'driver_curr': float(obj.driver_curr) if obj.driver_curr else None,
                    'a1_a2': float(obj.dsp_rxmsg_amplitudeEstimateA1 - obj.dsp_rxmsg_amplitudeEstimateA2) if (obj.dsp_rxmsg_amplitudeEstimateA1 and obj.dsp_rxmsg_amplitudeEstimateA2) else None,
                    'conc_solido': float(obj.pconc) if obj.pconc else None,
                    'corte_agua': float(obj.percent_cutWater64b) if obj.percent_cutWater64b else None,
                    'signal_gateway': float(obj.signal_strength_rxCoriolis) if obj.signal_strength_rxCoriolis else None,
                    'temp_gateway': float(obj.temperature_gateway) if obj.temperature_gateway else None,
                    
                    'timestamp': obj.created_at_iot.isoformat() if obj.created_at_iot else None,
                }
                
                # Enviar mensaje al grupo de WebSockets
                async_to_sync(channel_layer.group_send)(
                    room_group_name,
                    {
                        'type': 'datos_nuevos',
                        'datos': datos_websocket,
                        'timestamp': datos_websocket['timestamp']
                    }
                )
                logger.info(f"📡 Datos completos enviados por WebSocket a grupo: {room_group_name}")
            except Exception as e:
                # No fallar si hay error en WebSocket
                logger.error(f"❌ Error al enviar por WebSocket: {str(e)}")
            
            return Response({
                "success": True,
                "message": "Registro exitoso",
                "id": obj.id
            }, status=201)
        
        return Response({"success": False, "error": serializer.errors}, status=400)