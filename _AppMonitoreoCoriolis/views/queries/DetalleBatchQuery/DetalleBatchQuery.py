import logging
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import ConfiguracionCoeficientes
from _AppMonitoreoCoriolis.models import NodeRedData, BatchDetectado
from UTIL_LIB.conversiones import celsius_a_fahrenheit, lb_s_a_kg_min, lb_a_kg, g_cm3_a_kg_m3
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ
from UTIL_LIB.GUM_coriolis_simp import GUM
from UTIL_LIB.densidad60Modelo import rho15_from_rhoobs_api1124

# Configurar logging
logger = logging.getLogger(__name__)

class DetalleBatchQueryView(APIView):
    """
    CBV para obtener el detalle de un batch específico con datos para graficar
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, batch_id):
        try:
            # Obtener el batch
            batch = get_object_or_404(BatchDetectado, id=batch_id)
            
            # Obtener configuración para los límites del flujo másico
            config = None
            try:
                config = ConfiguracionCoeficientes.objects.get(systemId=batch.systemId)
                lim_inf = config.lim_inf_caudal_masico or 0  # En kg/min
                lim_sup = config.lim_sup_caudal_masico or 9999  # En kg/min
            except ConfiguracionCoeficientes.DoesNotExist:
                lim_inf = 0
                lim_sup = 9999
            
            # Extender el rango de datos 3 minutos antes y después para mejor contexto visual
            inicio_extendido = batch.fecha_inicio - timedelta(minutes=3)
            fin_extendido = batch.fecha_fin + timedelta(minutes=3)
            
            # Obtener todos los datos del intervalo extendido del batch
            datos = NodeRedData.objects.filter(
                systemId=batch.systemId,
                created_at_iot__gte=inicio_extendido,
                created_at_iot__lte=fin_extendido,
                created_at_iot__isnull=False  # Solo datos con timestamp IoT válido
            ).order_by('created_at_iot')
            
            if not datos.exists():
                return Response({
                    'success': False,
                    'error': 'No se encontraron datos para este batch'
                }, status=404)
            
            # Preparar datos para el gráfico y acumular Qm (dentro del batch)
            datos_grafico = []
            suma_qm_in = 0.0
            conteo_qm_in = 0
            for dato in datos:
                # Convertir UTC a hora de Colombia usando timestamp IoT
                fecha_colombia = dato.created_at_iot.astimezone(COLOMBIA_TZ)
                
                # Determinar si el punto está dentro del batch real o en el contexto extendido
                dentro_batch = batch.fecha_inicio <= dato.created_at_iot <= batch.fecha_fin
                
                # Convertir mass_rate de lb/sec a kg/min para consistencia
                mass_rate_kg_min = lb_s_a_kg_min(dato.mass_rate) if dato.mass_rate is not None else None
                
                # Convertir total_mass de lb a kg
                total_mass_kg = lb_a_kg(dato.total_mass) if dato.total_mass is not None else None
                
                # Convertir temperatura de °C a °F
                temperatura_f = celsius_a_fahrenheit(dato.coriolis_temperature) if dato.coriolis_temperature is not None else None
                
                registro = {
                    'timestamp': int(fecha_colombia.timestamp() * 1000),  # Para Chart.js
                    'fecha_hora': fecha_colombia.strftime('%d/%m %H:%M:%S'),
                    'mass_rate_lb_s': dato.mass_rate,  # Original en lb/s
                    'mass_rate_kg_min': mass_rate_kg_min,  # Convertido a kg/min
                    'total_mass_lb': dato.total_mass,  # Original en lb
                    'total_mass_kg': total_mass_kg,  # Convertido a kg
                    'coriolis_temperature_c': dato.coriolis_temperature,  # Original en °C
                    'coriolis_temperature_f': temperatura_f,  # Convertido a °F
                    'density': dato.density,
                    'pressure_out': dato.pressure_out,  # Presión de salida en psi
                    'driver_curr': dato.driver_curr,
                    'driver_curr_alm': dato.driver_curr_alm,
                    'dsp_rxmsg_amplitudeEstimateA1': dato.dsp_rxmsg_amplitudeEstimateA1,
                    'dsp_rxmsg_amplitudeEstimateA2': dato.dsp_rxmsg_amplitudeEstimateA2,
                    'dsp_rxmsg_driverAmplitude': dato.dsp_rxmsg_driverAmplitude,
                    'dsp_rxmsg_noiseEstimatedN1': dato.dsp_rxmsg_noiseEstimatedN1,
                    'dsp_rxmsg_noiseEstimatedN2': dato.dsp_rxmsg_noiseEstimatedN2,
                    'dentro_batch': dentro_batch  # Indica si está dentro del batch real
                }
                datos_grafico.append(registro)

                # Acumular Qm solo para puntos dentro del batch
                if dentro_batch and mass_rate_kg_min is not None:
                    suma_qm_in += mass_rate_kg_min
                    conteo_qm_in += 1

            # Qm promedio durante el batch
            Qm_prom = (suma_qm_in / conteo_qm_in) if conteo_qm_in > 0 else None

            # Diagnóstico del medidor (solo datos dentro del batch)
            datos_batch = [punto for punto in datos_grafico if punto['dentro_batch']]

            def calcular_metricas(clave):
                valores = [punto.get(clave) for punto in datos_batch if punto.get(clave) is not None]
                if not valores:
                    return {'ultimo': None, 'promedio': None, 'min': None, 'max': None}
                ultimo_valor = next(
                    (punto.get(clave) for punto in reversed(datos_batch) if punto.get(clave) is not None),
                    None
                )
                promedio = sum(valores) / len(valores) if valores else None
                return {
                    'ultimo': ultimo_valor,
                    'promedio': promedio,
                    'min': min(valores),
                    'max': max(valores)
                }

            metricas_cache = {}

            def obtener_metricas(clave):
                if clave not in metricas_cache:
                    metricas_cache[clave] = calcular_metricas(clave)
                return metricas_cache[clave]

            def calcular_max_desbalance_pct():
                max_ratio = None
                for punto in datos_batch:
                    a1 = punto.get('dsp_rxmsg_amplitudeEstimateA1')
                    a2 = punto.get('dsp_rxmsg_amplitudeEstimateA2')
                    if a1 is None or a2 is None:
                        continue
                    denominador = a1 + a2
                    if denominador == 0:
                        continue
                    ratio = abs(a1 - a2) / denominador
                    max_ratio = ratio if max_ratio is None else max(max_ratio, ratio)
                return max_ratio * 100 if max_ratio is not None else None

            alarma_driver = any(
                (punto.get('driver_curr_alm') is not None) and punto.get('driver_curr_alm') != 0
                for punto in datos_batch
            )

            parametros_diagnostico = [
                {
                    'id': 'driver_curr',
                    'label': 'Corriente del driver',
                    'unidad': 'mA',
                    'metricas': obtener_metricas('driver_curr'),
                    'en_alarma': alarma_driver
                },
                {
                    'id': 'dsp_rxmsg_amplitudeEstimateA1',
                    'label': 'Amplitud estimada A1',
                    'unidad': None,
                    'metricas': obtener_metricas('dsp_rxmsg_amplitudeEstimateA1'),
                    'en_alarma': False
                },
                {
                    'id': 'dsp_rxmsg_amplitudeEstimateA2',
                    'label': 'Amplitud estimada A2',
                    'unidad': None,
                    'metricas': obtener_metricas('dsp_rxmsg_amplitudeEstimateA2'),
                    'en_alarma': False
                },
                {
                    'id': 'dsp_rxmsg_driverAmplitude',
                    'label': 'Amplitud del driver',
                    'unidad': None,
                    'metricas': obtener_metricas('dsp_rxmsg_driverAmplitude'),
                    'en_alarma': False
                },
                {
                    'id': 'dsp_rxmsg_noiseEstimatedN1',
                    'label': 'Ruido estimado N1',
                    'unidad': None,
                    'metricas': obtener_metricas('dsp_rxmsg_noiseEstimatedN1'),
                    'en_alarma': False
                },
                {
                    'id': 'dsp_rxmsg_noiseEstimatedN2',
                    'label': 'Ruido estimado N2',
                    'unidad': None,
                    'metricas': obtener_metricas('dsp_rxmsg_noiseEstimatedN2'),
                    'en_alarma': False
                }
            ]

            # Configuración para diagnóstico
            diag_defaults = {
                'glp_density_ref': 0.55,
                'glp_density_tolerance_pct': 5.0,
                'driver_amp_multiplier': 1.3,
                'amp_imbalance_threshold_pct': 5.0
            }
            diag_config = {
                'glp_density_ref': getattr(config, 'diagnostic_glp_density_ref', None) if config else None,
                'glp_density_tolerance_pct': getattr(config, 'diagnostic_glp_density_tolerance_pct', None) if config else None,
                'driver_amp_base': getattr(config, 'diagnostic_driver_amp_base', None) if config else None,
                'driver_amp_multiplier': getattr(config, 'diagnostic_driver_amp_multiplier', None) if config else None,
                'n1_threshold': getattr(config, 'diagnostic_n1_threshold', None) if config else None,
                'n2_threshold': getattr(config, 'diagnostic_n2_threshold', None) if config else None,
                'amp_imbalance_threshold_pct': getattr(config, 'diagnostic_amp_imbalance_threshold_pct', None) if config else None,
            }

            glp_ref = diag_config['glp_density_ref'] if diag_config['glp_density_ref'] not in [None, 0] else diag_defaults['glp_density_ref']
            glp_tolerance_pct = diag_config['glp_density_tolerance_pct'] if diag_config['glp_density_tolerance_pct'] is not None else diag_defaults['glp_density_tolerance_pct']
            glp_variacion = max(glp_tolerance_pct, 0) / 100
            driver_amp_multiplier = diag_config['driver_amp_multiplier'] if diag_config['driver_amp_multiplier'] not in [None, 0] else diag_defaults['driver_amp_multiplier']
            amp_imbalance_threshold = diag_config['amp_imbalance_threshold_pct'] if diag_config['amp_imbalance_threshold_pct'] is not None else diag_defaults['amp_imbalance_threshold_pct']

            driver_amp_metricas = obtener_metricas('dsp_rxmsg_driverAmplitude')
            driver_amp_max = driver_amp_metricas['max']
            driver_amp_base = diag_config['driver_amp_base'] if diag_config['driver_amp_base'] not in [None, 0] else driver_amp_metricas['promedio']
            driver_amp_threshold = driver_amp_base * driver_amp_multiplier if driver_amp_base else None
            driver_amp_alto = driver_amp_threshold is not None and driver_amp_max is not None and driver_amp_max >= driver_amp_threshold

            n1_metricas = obtener_metricas('dsp_rxmsg_noiseEstimatedN1')
            n2_metricas = obtener_metricas('dsp_rxmsg_noiseEstimatedN2')
            n1_max = n1_metricas['max']
            n2_max = n2_metricas['max']
            n1_alert = diag_config['n1_threshold'] is not None and n1_max is not None and n1_max >= diag_config['n1_threshold']
            n2_alert = diag_config['n2_threshold'] is not None and n2_max is not None and n2_max >= diag_config['n2_threshold']
            ruido_configurado = (diag_config['n1_threshold'] is not None) or (diag_config['n2_threshold'] is not None)
            ruido_datos_disponibles = ruido_configurado and (n1_max is not None or n2_max is not None)
            ruido_alto = n1_alert or n2_alert

            desbalance_pct = calcular_max_desbalance_pct()
            desbalance_alert = desbalance_pct is not None and amp_imbalance_threshold is not None and desbalance_pct >= amp_imbalance_threshold

            densidad_prom = batch.densidad_prom
            porcentaje_agua = None
            if densidad_prom is not None and glp_ref not in [None, 0]:
                rho_agua = 1.0
                glp_superior = glp_ref * (1 + glp_variacion)
                if densidad_prom > glp_superior and rho_agua > glp_superior:
                    porcentaje_agua = min(100.0, max(0.0, ((densidad_prom - glp_superior) / (rho_agua - glp_superior)) * 100))
                else:
                    porcentaje_agua = 0.0

            vapor_detectado = driver_amp_alto and ruido_alto
            suciedad_detectada = driver_amp_alto and not ruido_alto and driver_amp_max is not None
            interferencia_detectada = ruido_alto and not driver_amp_alto

            def estado_detalle(alerta, datos_disponibles):
                if alerta:
                    return 'ALERTA'
                if not datos_disponibles:
                    return 'SIN_DATOS'
                return 'OK'

            detalles_multifase = []
            detalles_multifase.append({
                'id': 'agua',
                'titulo': '% Agua estimado',
                'estado': 'ALERTA' if porcentaje_agua is not None and porcentaje_agua > 1 else ('OK' if porcentaje_agua is not None else 'SIN_DATOS'),
                'valor': porcentaje_agua,
                'unidad': '%',
                'mensaje': 'Se calcula con regla de mezcla usando la densidad GLP configurada.'
            })
            detalles_multifase.append({
                'id': 'vapor',
                'titulo': 'Presencia de vapor/burbujas',
                'estado': estado_detalle(
                    vapor_detectado,
                    driver_amp_threshold is not None and ruido_datos_disponibles
                ),
                'valor': driver_amp_max,
                'unidad': 'mA',
                'mensaje': 'Driver Amp y ruido elevados indican burbujeo/dos fases o cavitación.'
            })
            detalles_multifase.append({
                'id': 'suciedad',
                'titulo': 'Suciedad o fluido viscoso',
                'estado': estado_detalle(
                    suciedad_detectada,
                    driver_amp_threshold is not None
                ),
                'valor': driver_amp_max,
                'unidad': 'mA',
                'mensaje': 'Driver Amp alto con ruido normal suele asociarse a suciedad o mayor viscosidad.'
            })
            ruido_maximo = None
            valores_ruido = [v for v in [n1_max, n2_max] if v is not None]
            if valores_ruido:
                ruido_maximo = max(valores_ruido)

            detalles_multifase.append({
                'id': 'interferencia',
                'titulo': 'Interferencia mecánica/eléctrica',
                'estado': estado_detalle(
                    interferencia_detectada,
                    ruido_datos_disponibles
                ),
                'valor': ruido_maximo,
                'unidad': None,
                'mensaje': 'Ruido elevado con Driver Amp normal sugiere interferencias externas.'
            })

            estado_multifase = 'SIN_DATOS'
            if any(det['estado'] == 'ALERTA' for det in detalles_multifase):
                estado_multifase = 'ALERTA'
            elif any(det['estado'] == 'OK' for det in detalles_multifase):
                estado_multifase = 'OK'

            indicadores_salud = [
                {
                    'id': 'driver_amp',
                    'label': 'Driver Amp (máx)',
                    'valor': driver_amp_max,
                    'umbral': driver_amp_threshold,
                    'estado': estado_detalle(driver_amp_alto, driver_amp_threshold is not None and driver_amp_max is not None),
                    'unidad': 'mA',
                    'descripcion': 'Se compara contra el valor base configurado.'
                },
                {
                    'id': 'desbalance',
                    'label': 'Desbalance A1/A2',
                    'valor': desbalance_pct,
                    'umbral': amp_imbalance_threshold,
                    'estado': estado_detalle(desbalance_alert, desbalance_pct is not None and amp_imbalance_threshold is not None),
                    'unidad': '%',
                    'descripcion': 'Calculado como |A1-A2|/(A1+A2).'
                },
                {
                    'id': 'n1',
                    'label': 'Ruido N1',
                    'valor': n1_max,
                    'umbral': diag_config['n1_threshold'],
                    'estado': estado_detalle(n1_alert, diag_config['n1_threshold'] is not None and n1_max is not None),
                    'unidad': None,
                    'descripcion': 'Comparado contra el umbral configurado.'
                },
                {
                    'id': 'n2',
                    'label': 'Ruido N2',
                    'valor': n2_max,
                    'umbral': diag_config['n2_threshold'],
                    'estado': estado_detalle(n2_alert, diag_config['n2_threshold'] is not None and n2_max is not None),
                    'unidad': None,
                    'descripcion': 'Comparado contra el umbral configurado.'
                },
            ]

            mensajes_multifase = []
            if porcentaje_agua is None:
                mensajes_multifase.append('Sin densidad promedio para estimar porcentaje de agua.')
            elif porcentaje_agua > 1:
                mensajes_multifase.append(f'Densidad promedio superior a la referencia GLP (+{porcentaje_agua:.1f}%). Posible presencia de agua.')

            if vapor_detectado:
                mensajes_multifase.append('Driver Amp y ruido elevados: patrón consistente con vapor/burbujas o cavitación.')
            if suciedad_detectada:
                mensajes_multifase.append('Driver Amp elevado con ruido normal: revisar posibles sólidos o fluido más viscoso.')
            if interferencia_detectada:
                mensajes_multifase.append('Ruido elevado con Driver Amp normal: revisar posibles interferencias mecánicas/eléctricas.')

            mensajes_salud = []
            if desbalance_alert:
                mensajes_salud.append(f'Desbalance entre tubos superior a {amp_imbalance_threshold:.1f}% (máx observado {desbalance_pct:.1f}%).')
            if n1_alert or n2_alert:
                mensajes_salud.append('Ruido N1/N2 excede el umbral configurado.')

            estado_salud = 'SIN_DATOS'
            if any(ind['estado'] == 'ALERTA' for ind in indicadores_salud):
                estado_salud = 'ALERTA'
            elif any(ind['estado'] == 'OK' for ind in indicadores_salud):
                estado_salud = 'OK'

            estado_general = 'SIN_DATOS'
            if estado_multifase == 'ALERTA' or estado_salud == 'ALERTA':
                estado_general = 'ALERTA'
            elif estado_multifase == 'SIN_DATOS' and estado_salud == 'SIN_DATOS':
                estado_general = 'SIN_DATOS'
            else:
                estado_general = 'OK'

            mensajes_diagnostico = mensajes_multifase + mensajes_salud
            if not mensajes_diagnostico and estado_general != 'SIN_DATOS':
                mensajes_diagnostico = ['Sin anomalías detectadas en los parámetros configurados.']
            elif not mensajes_diagnostico:
                mensajes_diagnostico = ['No se encontraron lecturas suficientes para un diagnóstico.']

            alarmas_detectadas = []
            if porcentaje_agua is not None and porcentaje_agua > 1:
                alarmas_detectadas.append('agua')
            if vapor_detectado:
                alarmas_detectadas.append('vapor')
            if suciedad_detectada:
                alarmas_detectadas.append('suciedad')
            if interferencia_detectada:
                alarmas_detectadas.append('interferencia')
            if desbalance_alert:
                alarmas_detectadas.append('desbalance')
            if n1_alert:
                alarmas_detectadas.append('n1')
            if n2_alert:
                alarmas_detectadas.append('n2')
            if alarma_driver:
                alarmas_detectadas.append('driver_curr')

            diagnostico_batch = {
                'estado_general': estado_general,
                'mensajes': mensajes_diagnostico,
                'parametros': parametros_diagnostico,
                'alarmas_detectadas': alarmas_detectadas,
                'multifase': {
                    'estado': estado_multifase,
                    'porcentaje_agua': porcentaje_agua,
                    'densidad_promedio': densidad_prom,
                    'densidad_glp_referencia': glp_ref,
                    'variacion_glp_pct': glp_tolerance_pct,
                    'detalles': detalles_multifase
                },
                'salud_medidor': {
                    'estado': estado_salud,
                    'indicadores': indicadores_salud,
                    'mensajes': mensajes_salud
                }
            }

            # Calcular densidad a 60°F (rho15) para usar en GUM
            rho15 = None
            try:
                if batch.densidad_prom is not None and batch.temperatura_coriolis_prom is not None:
                    rho_obs = g_cm3_a_kg_m3(batch.densidad_prom)  # g/cc -> kg/m³
                    T_obs_C = batch.temperatura_coriolis_prom
                    rho15, _gamma60 = rho15_from_rhoobs_api1124(rho_obs, T_obs_C)
            except Exception as e:
                logger.warning(f"No fue posible calcular rho15 para batch {batch_id}: {e}")

                # Preparar entradas para motor GUM (usando nombres exactos)
            incertidumbre_result = None
            try:
                # Valores medidos/promedios del batch
                Tl = celsius_a_fahrenheit(batch.temperatura_coriolis_prom) if batch.temperatura_coriolis_prom is not None else None
                Pl = batch.pressure_out_prom
                Masa = batch.mass_total  # ya en kg según modelo

                # Variables de configuración (Incertidumbre) desde ConfiguracionCoeficientes
                # Pueden ser None si no están configuradas; el motor GUM validará y podría lanzar error
                gum_input = {
                    'dl': rho15,  # usar densidad a 60°F (kg/m³) calculada en backend
                    'MF': getattr(config, 'mf', None),
                    'vis': getattr(config, 'vis', None),
                    'deltavis': getattr(config, 'deltavis', None),
                    'DN': getattr(config, 'dn', None),
                    'ucalDens': getattr(config, 'ucal_dens', None),
                    'kcalDens': getattr(config, 'kcal_dens', None),
                    'tipdens': getattr(config, 'tipdens', None),
                    'desvdens': getattr(config, 'desv_dens', None),
                    'ucalMet': getattr(config, 'ucal_met', None),
                    'kcalMet': getattr(config, 'kcal_met', None),
                    'esisMet': getattr(config, 'esis_met', None),
                    'ucartaMet': getattr(config, 'ucarta_met', None),
                    'zeroStab': getattr(config, 'zero_stab', None),
                    # Backend-provided (temperatura en °F, presión psi, masa kg, Qm promedio kg/min)
                    'Tl': Tl,
                    'Pl': Pl,
                    'Masa': Masa,
                    'Qm': Qm_prom,
                    # Constantes/fijos
                    'tipoMet': 'COR',
                    'product': 'GLP'
                }

                # Fallbacks / saneamiento de entradas
                # MF por defecto 1 si no configurado
                if gum_input['MF'] is None or gum_input['MF'] == 0:
                    gum_input['MF'] = 1
                # DN por defecto 1 si no configurado
                if gum_input['DN'] is None or gum_input['DN'] == 0:
                    gum_input['DN'] = 1
                # Convertir Qm (kg/min) a kg/h si existe
                if gum_input['Qm'] is not None:
                    gum_input['Qm'] = gum_input['Qm'] * 60.0
                # Reemplazar None numéricos por 0 para evitar TypeError dentro de operaciones
                for clave in ['vis','deltavis','ucalDens','kcalDens','desvdens','ucalMet','kcalMet','esisMet','ucartaMet','zeroStab','Tl','Pl']:
                    if gum_input[clave] is None:
                        gum_input[clave] = 0

                # Verificación mínima antes de cálculo
                if gum_input['Masa'] and gum_input['Masa'] > 0 and gum_input['dl'] and gum_input['dl'] > 0:
                    incertidumbre_result = GUM(gum_input)
                else:
                    logger.info(f"Incertidumbre omitida: Masa ({gum_input['Masa']}), dl ({gum_input['dl']}) insuficientes para batch {batch_id}")
            except Exception as e:
                logger.warning(f"No fue posible calcular incertidumbre GUM para batch {batch_id}: {e}")
            
            return Response({
                'success': True,
                'batch_info': {
                    'id': batch.id,
                    'sistema_tag': batch.systemId.tag,
                    'ubicación': batch.systemId.ubicacion.nombre if batch.systemId.ubicacion else "Sin ubicación",
                    'identificador_medidor': batch.systemId.identificacion_medidor if batch.systemId.identificacion_medidor else "N/A",
                    'fecha_inicio': batch.fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin': batch.fecha_fin.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'mass_total_kg': batch.mass_total,
                    'vol_total': batch.vol_total,
                    'presion_out_prom': batch.pressure_out_prom,
                    'temperatura_coriolis_prom_c': batch.temperatura_coriolis_prom,  # Original en °C
                    'temperatura_coriolis_prom_f': celsius_a_fahrenheit(batch.temperatura_coriolis_prom) if batch.temperatura_coriolis_prom is not None else None,  # Convertido a °F
                    'densidad_prom': batch.densidad_prom,
                    'qm_promedio_kg_min': Qm_prom,
                    'duracion_minutos': batch.duracion_minutos,
                    'total_registros': batch.total_registros,
                    # Timestamps para marcar límites del batch en la gráfica
                    'timestamp_inicio': int(batch.fecha_inicio.astimezone(COLOMBIA_TZ).timestamp() * 1000),
                    'timestamp_fin': int(batch.fecha_fin.astimezone(COLOMBIA_TZ).timestamp() * 1000)
                },
                'datos_grafico': datos_grafico,
                'total_datos': len(datos_grafico),
                # Límites para las líneas horizontales en el gráfico
                'lim_inf_caudal_masico': lim_inf,
                'lim_sup_caudal_masico': lim_sup,
                # Resultados de Incertidumbre (si se pudo calcular)
                'incertidumbre': incertidumbre_result,
                # Diagnóstico del medidor
                'diagnostico': diagnostico_batch
            })
            
        except Exception as e:
            logger.error(f"Error en DetalleBatchQueryView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error al obtener detalle del batch: {str(e)}'
            }, status=500)
