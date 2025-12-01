import logging
import hashlib
import pytz
from datetime import datetime
from django.utils import timezone as django_timezone
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes
from _AppMonitoreoCoriolis.models import NodeRedData, BatchDetectado
from UTIL_LIB.conversiones import lb_s_a_kg_min, lb_a_kg, cm3_a_gal
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ

# Configurar logging
logger = logging.getLogger(__name__)

class DetectarBatchesCommandView(APIView):
    """
    CBV para detectar batches en un rango de fechas específico
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, sistema_id):
        try:
            # Obtener parámetros
            fecha_inicio_str = request.data.get('fecha_inicio')
            fecha_fin_str = request.data.get('fecha_fin')
            
            if not fecha_inicio_str or not fecha_fin_str:
                return Response({
                    'success': False,
                    'error': 'Las fechas de inicio y fin son obligatorias'
                }, status=400)
            
            # Verificar que el sistema existe
            sistema = Sistema.objects.get(id=sistema_id)
            
            # Obtener límites de configuración (solo para lim_inf y lim_sup)
            try:
                config = ConfiguracionCoeficientes.objects.get(systemId=sistema)
                lim_inf = config.lim_inf_caudal_masico  # En kg/min
                lim_sup = config.lim_sup_caudal_masico  # En kg/min
                # YA NO usar vol_minimo ni time_finished_batch de configuración
                # Estos valores ahora vienen dinámicamente de cada registro NodeRedData
            except ConfiguracionCoeficientes.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'No se encontró configuración de límites para este sistema'
                }, status=400)
            
            # Parsear fechas con formato datetime (igual que las queries históricas)
            try:
                # Intentar formato con fecha y hora: "2025-10-16T00:00:00"
                fecha_inicio_naive = datetime.strptime(fecha_inicio_str, '%Y-%m-%dT%H:%M:%S')
                fecha_fin_naive = datetime.strptime(fecha_fin_str, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                try:
                    # Fallback a formato solo fecha: "2025-10-16"
                    fecha_inicio_naive = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                    fecha_fin_naive = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
                    # Establecer horas para cubrir todo el rango del día
                    fecha_inicio_naive = fecha_inicio_naive.replace(hour=0, minute=0, second=0, microsecond=0)
                    fecha_fin_naive = fecha_fin_naive.replace(hour=23, minute=59, second=59, microsecond=999999)
                except ValueError:
                    return Response({
                        'success': False,
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS'
                    }, status=400)
            
            # Asumir que las fechas del frontend están en hora de Colombia y convertir a UTC
            fecha_inicio_colombia = COLOMBIA_TZ.localize(fecha_inicio_naive)
            fecha_fin_colombia = COLOMBIA_TZ.localize(fecha_fin_naive)
            
            # Convertir a UTC para consultas de base de datos (igual que otras queries)
            fecha_inicio = fecha_inicio_colombia.astimezone(pytz.UTC)
            fecha_fin = fecha_fin_colombia.astimezone(pytz.UTC)
            
            # IMPORTANTE: Agregar margen de tiempo después de fecha_fin para detectar batches
            # que cruzan medianoche. Esto permite que si un batch inicia el día consultado
            # pero termina después de medianoche, se pueda detectar el cambio de día y cerrar
            # correctamente el batch del día anterior.
            from datetime import timedelta
            margen_deteccion = timedelta(hours=2)  # 2 horas después de fecha_fin
            fecha_fin_con_margen = fecha_fin + margen_deteccion
            
            # Log para debugging de zona horaria
            logger.info(f"Fechas Colombia - Inicio: {fecha_inicio_colombia} | Fin: {fecha_fin_colombia}")
            logger.info(f"Fechas UTC (para DB) - Inicio: {fecha_inicio} | Fin: {fecha_fin}")
            logger.info(f"Fecha fin con margen de detección: {fecha_fin_con_margen} (UTC) - Margen: {margen_deteccion.total_seconds()/3600} horas")
            logger.info(f"Input recibido - fecha_inicio_str: '{fecha_inicio_str}', fecha_fin_str: '{fecha_fin_str}'")
            
            # Obtener datos del rango de fechas CON MARGEN, ordenados por fecha IoT
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at_iot__gte=fecha_inicio,
                created_at_iot__lte=fecha_fin_con_margen,  # Usar fecha con margen
                created_at_iot__isnull=False  # Solo datos con timestamp IoT válido
            ).order_by('created_at_iot')
            
            logger.info(f"📊 Datos consultados: {datos.count()} registros (incluye margen para detección de medianoche)")
            
            if not datos.exists():
                return Response({
                    'success': False,
                    'error': 'No se encontraron datos en el rango de fechas especificado'
                }, status=404)
            
            # Ejecutar algoritmo de detección de batches con perfil dinámico
            batches_detectados = self._detectar_batches_con_perfil_dinamico(datos, lim_inf, lim_sup, sistema)
            
            # Guardar batches en la base de datos con prevención de duplicados
            batches_guardados = []
            batches_existentes = 0
            
            for batch_data in batches_detectados:
                # Generar hash para este batch usando el perfil dinámico que se usó
                hash_batch = self._generar_hash_batch(
                    batch_data['fecha_inicio'],
                    batch_data['fecha_fin'], 
                    sistema_id,
                    batch_data['vol_minimo_usado'],
                    batch_data['time_finished_usado']
                )
                
                try:
                    # Intentar crear el batch con el hash único
                    batch = BatchDetectado.objects.create(
                        systemId=sistema,
                        fecha_inicio=batch_data['fecha_inicio'],
                        fecha_fin=batch_data['fecha_fin'],
                        vol_total=batch_data['vol_total'],
                        mass_total=batch_data['mass_total'],
                        temperatura_coriolis_prom=batch_data['temperatura_coriolis_prom'],
                        densidad_prom=batch_data['densidad_prom'],
                        pressure_out_prom=batch_data.get('pressure_out_prom'),
                        hash_identificacion=hash_batch,
                        perfil_lim_inf_caudal=lim_inf,
                        perfil_lim_sup_caudal=lim_sup,
                        perfil_vol_minimo=batch_data['vol_minimo_usado'],
                        duracion_minutos=batch_data['duracion_minutos'],
                        total_registros=batch_data['total_registros'],
                        time_finished_batch=batch_data['time_finished_usado']
                    )
                except IntegrityError:
                    # El batch ya existe (por el hash único), buscar el existente
                    logger.info(f"Batch ya existe con hash {hash_batch[:16]}...")
                    batch = BatchDetectado.objects.get(hash_identificacion=hash_batch)
                    batches_existentes += 1
                batches_guardados.append({
                    'id': batch.id,
                    'fecha_inicio': batch.fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin': batch.fecha_fin.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'vol_total': round(batch.vol_total, 2),
                    'mass_total': round(batch.mass_total, 2),
                    'temperatura_coriolis_prom': round(batch.temperatura_coriolis_prom, 2),
                    'densidad_prom': round(batch.densidad_prom, 10),
                    'pressure_out_prom': round(batch.pressure_out_prom, 2) if batch.pressure_out_prom else None,
                    'duracion_minutos': round(batch.duracion_minutos, 2),
                    'total_registros': batch.total_registros,
                    'perfil_lim_inf': batch.perfil_lim_inf_caudal,
                    'perfil_lim_sup': batch.perfil_lim_sup_caudal,
                    'perfil_vol_min': batch.perfil_vol_minimo
                })
            
            # Obtener TODOS los batches existentes en el rango de fechas (no solo los recién detectados)
            todos_batches = BatchDetectado.objects.filter(
                systemId=sistema,
                fecha_inicio__gte=fecha_inicio,
                fecha_fin__lte=fecha_fin
            ).order_by('-fecha_inicio')
            
            batches_completos = []
            for batch in todos_batches:
                batches_completos.append({
                    'id': batch.id,
                    'fecha_inicio': batch.fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin': batch.fecha_fin.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'vol_total': round(batch.vol_total, 2),
                    'mass_total': round(batch.mass_total, 2),
                    'temperatura_coriolis_prom': round(batch.temperatura_coriolis_prom, 2),
                    'densidad_prom': round(batch.densidad_prom, 10),
                    'pressure_out_prom': round(batch.pressure_out_prom, 2) if batch.pressure_out_prom else None,
                    'duracion_minutos': round(batch.duracion_minutos, 2),
                    'total_registros': batch.total_registros,
                    'perfil_lim_inf': batch.perfil_lim_inf_caudal or 0,
                    'perfil_lim_sup': batch.perfil_lim_sup_caudal or 0,
                    'perfil_vol_min': batch.perfil_vol_minimo or 0
                })
            
            return Response({
                'success': True,
                'batches_detectados': len(batches_completos),
                'batches_nuevos': len(batches_guardados) - batches_existentes,
                'batches_existentes': batches_existentes,
                'batches': batches_completos,
                'configuracion_usada': {
                    'lim_inf_caudal_masico': lim_inf,
                    'lim_sup_caudal_masico': lim_sup,
                    'nota': 'vol_detect_batch y time_closed_batch se usan dinámicamente de cada registro NodeRedData'
                },
                'rango_analizado': {
                    'fecha_inicio': fecha_inicio.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin': fecha_fin.astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                    'total_registros': datos.count()
                }
            })
            
        except Sistema.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Sistema no encontrado'
            }, status=404)
        except ValueError as e:
            return Response({
                'success': False,
                'error': f'Error en formato de fecha: {str(e)}'
            }, status=400)
        except Exception as e:
            logger.error(f"Error en DetectarBatchesCommandView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
    
    def _detectar_batches_con_perfil_dinamico(self, datos, lim_inf, lim_sup, sistema):
        """
        Lógica de detección con PERFIL DINÁMICO del PRIMER DATO:
        - Cada batch captura vol_detect_batch y time_closed_batch del PRIMER dato que lo inicia
        - El perfil se mantiene constante hasta que el batch se cierra
        - Detecta cuando caudal cambia de 0 a > 0 (inicio de batch)
        - Cuando caudal vuelve a 0, espera time_closed_batch minutos antes de cerrar
        - Si caudal sube antes del tiempo de espera, continúa el batch
        - Compara masa total del último punto vs primer punto
        - Si la diferencia supera vol_detect_batch, es batch válido
        
        Args:
            datos: QuerySet de NodeRedData ordenado por created_at_iot
            lim_inf: Límite inferior de caudal másico (kg/min) - SOLO PARA REFERENCIA
            lim_sup: Límite superior de caudal másico (kg/min) - SOLO PARA REFERENCIA
            sistema: Instancia del Sistema
        """
        batches = []
        en_batch = False
        inicio_batch = None
        primer_dato = None
        datos_batch = []
        punto_anterior = None
        tiempo_cero_inicio = None
        ultimo_dato_con_flujo = None
        
        # Perfil capturado del PRIMER dato del batch (se mantiene constante)
        vol_minimo_batch = None
        time_finished_batch_actual = None

        logger.info(f"🔍 Iniciando detección con PERFIL DINÁMICO del primer dato de cada batch")

        for dato in datos:
            mass_rate_raw = dato.mass_rate  # En lb/sec
            total_mass = dato.total_mass
            total_volume = dato.total_volume
            timestamp_actual = dato.created_at_iot
            
            # LOG: Mostrar timestamp de cada registro para debugging
            logger.debug(f"📅 Procesando registro: {timestamp_actual} | mass_rate: {mass_rate_raw} lb/sec")
            
            # Verificar que tenemos los datos necesarios
            if mass_rate_raw is None or total_mass is None or total_volume is None:
                logger.debug(f"⚠️ Saltando registro con datos faltantes en {timestamp_actual}")
                continue
                
            # Convertir mass_rate de lb/sec a kg/min
            mass_rate_kg_min = lb_s_a_kg_min(mass_rate_raw)
            logger.debug(f"🔄 Convertido: {mass_rate_kg_min:.3f} kg/min")
            
            # LÓGICA DINÁMICA: Detectar cambio de 0 a > 0 y manejar tiempo de espera con perfil del primer dato
            if mass_rate_kg_min > 0:
                if not en_batch:
                    # 🎯 CAPTURAR PERFIL DEL PRIMER DATO
                    vol_detect = dato.vol_detect_batch
                    time_closed = dato.time_closed_batch
                    
                    # Validar que el dato tiene perfil válido
                    if vol_detect is None or time_closed is None:
                        logger.warning(f"⚠️ Dato sin perfil válido en {dato.created_at_local}: vol_detect={vol_detect}, time_closed={time_closed} - IGNORANDO")
                        continue
                    
                    # Capturar perfil para este batch
                    vol_minimo_batch = vol_detect
                    time_finished_batch_actual = time_closed
                    
                    # Iniciar nuevo batch - usar punto anterior como referencia inicial
                    en_batch = True
                    inicio_batch = dato.created_at_iot
                    tiempo_cero_inicio = None
                    
                    # Si tenemos punto anterior (donde flujo = 0), usarlo como referencia
                    if punto_anterior is not None:
                        primer_dato = punto_anterior
                        logger.info(f"✅ Iniciando batch en {inicio_batch}, usando punto anterior como referencia")
                        logger.info(f"   Punto inicial (flujo=0): masa={primer_dato.total_mass} lb, volumen={primer_dato.total_volume} cm³")
                        logger.info(f"   🎯 PERFIL CAPTURADO: vol_detect={vol_minimo_batch:.2f} kg, time_closed={time_finished_batch_actual:.2f} min")
                    else:
                        primer_dato = dato
                        logger.info(f"✅ Iniciando batch en {inicio_batch}, sin punto anterior disponible")
                        logger.info(f"   🎯 PERFIL CAPTURADO: vol_detect={vol_minimo_batch:.2f} kg, time_closed={time_finished_batch_actual:.2f} min")
                    
                    datos_batch = [dato]
                    ultimo_dato_con_flujo = dato
                    logger.debug(f"Flujo actual: {mass_rate_kg_min:.2f} kg/min, masa actual: {total_mass} lb, volumen actual: {total_volume} cm³")
                else:
                    # Continuar batch - el flujo volvió a subir, reiniciar contador de tiempo en cero
                    
                    # 🌙 VERIFICAR CAMBIO DE DÍA - Cerrar batch del día anterior si cruza medianoche
                    fecha_inicio_batch_colombia = primer_dato.created_at_iot.astimezone(COLOMBIA_TZ).date()
                    fecha_dato_actual_colombia = dato.created_at_iot.astimezone(COLOMBIA_TZ).date()
                    
                    if fecha_inicio_batch_colombia != fecha_dato_actual_colombia:
                        # HAY CAMBIO DE DÍA - Cerrar batch del día anterior antes de continuar
                        logger.info(f"🌙 CAMBIO DE DÍA DETECTADO: {fecha_inicio_batch_colombia} -> {fecha_dato_actual_colombia}")
                        logger.info(f"   Cerrando batch del día anterior y comenzando nuevo batch")
                        
                        # Encontrar el último dato del día anterior (antes de medianoche)
                        ultimo_dato_dia_anterior = None
                        for d in reversed(datos_batch):
                            if d.created_at_iot.astimezone(COLOMBIA_TZ).date() == fecha_inicio_batch_colombia:
                                ultimo_dato_dia_anterior = d
                                break
                        
                        if ultimo_dato_dia_anterior is not None:
                            # Calcular masa y volumen hasta el último dato del día anterior
                            masa_inicial_lb = primer_dato.total_mass
                            masa_final_lb = ultimo_dato_dia_anterior.total_mass
                            diferencia_masa_lb = masa_final_lb - masa_inicial_lb
                            diferencia_masa_kg = lb_a_kg(diferencia_masa_lb)
                            
                            volumen_inicial_cm3 = primer_dato.total_volume
                            volumen_final_cm3 = ultimo_dato_dia_anterior.total_volume
                            diferencia_volumen_cm3 = volumen_final_cm3 - volumen_inicial_cm3
                            diferencia_volumen_gal = cm3_a_gal(diferencia_volumen_cm3)
                            
                            logger.info(f"   Batch día anterior: {primer_dato.created_at_iot} - {ultimo_dato_dia_anterior.created_at_iot}")
                            logger.info(f"   Masa: {diferencia_masa_kg:.2f} kg, Vol: {diferencia_volumen_gal:.3f} gal")
                            
                            # Validar con volumen mínimo
                            if diferencia_masa_kg >= vol_minimo_batch:
                                # Calcular datos del batch del día anterior
                                datos_dia_anterior = [d for d in datos_batch if d.created_at_iot.astimezone(COLOMBIA_TZ).date() == fecha_inicio_batch_colombia]
                                
                                temperaturas = [d.coriolis_temperature for d in datos_dia_anterior if d.coriolis_temperature is not None]
                                densidades = [d.density for d in datos_dia_anterior if d.density is not None]
                                presiones = [d.pressure_out for d in datos_dia_anterior if d.pressure_out is not None]
                                temp_prom = sum(temperaturas) / len(temperaturas) if temperaturas else 0
                                dens_prom = sum(densidades) / len(densidades) if densidades else 0
                                pres_prom = sum(presiones) / len(presiones) if presiones else None
                                
                                batches.append({
                                    'fecha_inicio': primer_dato.created_at_iot,
                                    'fecha_fin': ultimo_dato_dia_anterior.created_at_iot,
                                    'vol_total': diferencia_volumen_gal,
                                    'mass_total': diferencia_masa_kg,
                                    'temperatura_coriolis_prom': temp_prom,
                                    'densidad_prom': dens_prom,
                                    'pressure_out_prom': pres_prom,
                                    'duracion_minutos': (ultimo_dato_dia_anterior.created_at_iot - primer_dato.created_at_iot).total_seconds() / 60,
                                    'total_registros': len(datos_dia_anterior),
                                    'vol_minimo_usado': vol_minimo_batch,
                                    'time_finished_usado': time_finished_batch_actual
                                })
                                logger.info(f"✅ Batch del día anterior guardado por cambio de día")
                            else:
                                logger.info(f"❌ Batch del día anterior descartado: {diferencia_masa_kg:.2f} kg < {vol_minimo_batch} kg")
                        
                        # Reiniciar estado - NO iniciar batch del nuevo día automáticamente
                        # El batch del nuevo día se iniciará cuando el algoritmo detecte flujo > 0 sin estar en batch
                        en_batch = False
                        inicio_batch = None
                        primer_dato = None
                        datos_batch = []
                        tiempo_cero_inicio = None
                        ultimo_dato_con_flujo = None
                        vol_minimo_batch = None
                        time_finished_batch_actual = None
                        logger.info(f"   Estado reiniciado. El batch del nuevo día se iniciará cuando se detecte según la lógica normal")
                        continue
                    
                    # No hay cambio de día, continuar batch normalmente
                    datos_batch.append(dato)
                    ultimo_dato_con_flujo = dato
                    
                    # Si había un contador de tiempo en cero, reiniciarlo
                    if tiempo_cero_inicio is not None:
                        tiempo_antes_subir = timestamp_actual - tiempo_cero_inicio
                        minutos_antes_subir = tiempo_antes_subir.total_seconds() / 60
                        logger.info(f"🟢 FLUJO VOLVIÓ A SUBIR - Continuando batch")
                        logger.info(f"⏱️ Tiempo que estuvo en cero: {minutos_antes_subir:.3f} min (límite: {time_finished_batch_actual} min)")
                        logger.info(f"🔄 Reiniciando contador de tiempo en cero")
                        tiempo_cero_inicio = None  # Reiniciar porque el flujo volvió a subir
                    else:
                        logger.debug(f"➕ Agregando datos al batch en curso (timestamp: {timestamp_actual})")
            else:
                # mass_rate <= 0: verificar tiempo de espera si estaba en batch
                if en_batch:
                    if tiempo_cero_inicio is None:
                        # Primera vez que el flujo cae a cero, iniciar contador
                        tiempo_cero_inicio = timestamp_actual
                        logger.info(f"🔴 FLUJO CAYÓ A CERO - Iniciando contador de tiempo")
                        logger.info(f"⏱️ Tiempo inicio cero: {tiempo_cero_inicio}")
                        logger.info(f"⏳ Esperando {time_finished_batch_actual} minutos para cerrar batch")
                    else:
                        # Verificar si ya pasó el tiempo de espera
                        tiempo_transcurrido = timestamp_actual - tiempo_cero_inicio
                        minutos_en_cero = tiempo_transcurrido.total_seconds() / 60
                        
                        logger.debug(f"⏰ Registro actual: {timestamp_actual}")
                        logger.debug(f"🕐 Tiempo desde inicio cero: {tiempo_transcurrido}")
                        logger.debug(f"📊 Minutos transcurridos: {minutos_en_cero:.3f} min / {time_finished_batch_actual} min")
                        
                        if minutos_en_cero >= time_finished_batch_actual:
                            # Ha pasado el tiempo de espera, cerrar el batch
                            fin_batch = tiempo_cero_inicio  # Usar el momento cuando empezó a estar en cero
                            
                            logger.info(f"✅ TIEMPO SUPERADO - Cerrando batch después de {minutos_en_cero:.3f} min en cero")
                            logger.info(f"🏁 Batch se cierra en: {fin_batch}")
                            
                            # Calcular diferencias de masa y volumen entre último dato con flujo y primer punto
                            if primer_dato and ultimo_dato_con_flujo:
                                # Cálculos de masa
                                masa_inicial_lb = primer_dato.total_mass
                                masa_final_lb = ultimo_dato_con_flujo.total_mass
                                diferencia_masa_lb = masa_final_lb - masa_inicial_lb
                                diferencia_masa_kg = lb_a_kg(diferencia_masa_lb)
                                
                                # Cálculos de volumen (convertir de cm³ a galones)
                                volumen_inicial_cm3 = primer_dato.total_volume
                                volumen_final_cm3 = ultimo_dato_con_flujo.total_volume
                                diferencia_volumen_cm3 = volumen_final_cm3 - volumen_inicial_cm3
                                diferencia_volumen_gal = cm3_a_gal(diferencia_volumen_cm3)
                                
                                logger.debug(f"Cerrando batch después de {minutos_en_cero:.2f} min en cero (límite: {time_finished_batch_actual} min)")
                                logger.debug(f"Masa inicial (punto en 0): {masa_inicial_lb:.2f} lb en {primer_dato.created_at_iot}")
                                logger.debug(f"Masa final (último punto >0): {masa_final_lb:.2f} lb en {ultimo_dato_con_flujo.created_at_iot}")
                                logger.debug(f"Diferencia masa: {diferencia_masa_lb:.2f} lb = {diferencia_masa_kg:.2f} kg")
                                logger.debug(f"Volumen inicial: {volumen_inicial_cm3:.2f} cm³, Volumen final: {volumen_final_cm3:.2f} cm³")
                                logger.debug(f"Diferencia volumen: {diferencia_volumen_cm3:.2f} cm³ = {diferencia_volumen_gal:.3f} gal")
                                
                                # Solo guardar si la diferencia de masa supera el volumen mínimo (criterio de validación)
                                if diferencia_masa_kg >= vol_minimo_batch:
                                    # Calcular promedios
                                    temperaturas = [d.coriolis_temperature for d in datos_batch if d.coriolis_temperature is not None]
                                    densidades = [d.density for d in datos_batch if d.density is not None]
                                    presiones = [d.pressure_out for d in datos_batch if d.pressure_out is not None]
                                    temp_prom = sum(temperaturas) / len(temperaturas) if temperaturas else 0
                                    dens_prom = sum(densidades) / len(densidades) if densidades else 0
                                    pres_prom = sum(presiones) / len(presiones) if presiones else None
                                    
                                    batches.append({
                                        'fecha_inicio': primer_dato.created_at_iot,
                                        'fecha_fin': fin_batch,
                                        'vol_total': diferencia_volumen_gal,
                                        'mass_total': diferencia_masa_kg,
                                        'temperatura_coriolis_prom': temp_prom,
                                        'densidad_prom': dens_prom,
                                        'pressure_out_prom': pres_prom,
                                        'duracion_minutos': (fin_batch - primer_dato.created_at_iot).total_seconds() / 60,
                                        'total_registros': len(datos_batch),
                                        'vol_minimo_usado': vol_minimo_batch,
                                        'time_finished_usado': time_finished_batch_actual
                                    })
                                    logger.info(f"Batch guardado después de {minutos_en_cero:.2f} min en cero: {primer_dato.created_at_iot} - {fin_batch}, Vol: {diferencia_volumen_gal:.3f} gal, Masa: {diferencia_masa_kg:.2f} kg")
                                else:
                                    logger.debug(f"Batch descartado: {diferencia_masa_kg:.2f} kg < {vol_minimo_batch} kg")
                            
                            # Reiniciar estado
                            en_batch = False
                            inicio_batch = None
                            primer_dato = None
                            datos_batch = []
                            tiempo_cero_inicio = None
                            ultimo_dato_con_flujo = None
                            # 🔄 Resetear perfil para el siguiente batch
                            vol_minimo_batch = None
                            time_finished_batch_actual = None
                        else:
                            # Si no ha pasado el tiempo, seguir esperando
                            tiempo_restante = time_finished_batch_actual - minutos_en_cero
                            logger.debug(f"⏳ Esperando... Faltan {tiempo_restante:.3f} min para cerrar batch")
                else:
                    # No hay batch activo, guardar como punto anterior
                    tiempo_cero_inicio = None
                
                # Guardar este punto como posible referencia para el próximo batch
                punto_anterior = dato

        # IMPORTANTE: La lógica de tiempo de cierre (time_closed_batch) se mantiene en el loop principal
        # Esta sección solo maneja el batch que queda abierto al TERMINAR el rango de fechas consultado
        
        # Si termina con un batch abierto al final del rango de fechas
        if en_batch and datos_batch and primer_dato is not None and ultimo_dato_con_flujo is not None:
            # Verificar si el último dato procesado tiene flujo activo (mass_rate > 0)
            ultimo_dato = datos_batch[-1] if datos_batch else None
            ultimo_mass_rate_kg_min = lb_s_a_kg_min(ultimo_dato.mass_rate) if ultimo_dato and ultimo_dato.mass_rate is not None else 0
            
            # Verificar si hay cambio de día entre el inicio del batch y el último dato
            fecha_inicio_batch_colombia = primer_dato.created_at_iot.astimezone(COLOMBIA_TZ).date()
            fecha_ultimo_dato_colombia = ultimo_dato.created_at_iot.astimezone(COLOMBIA_TZ).date() if ultimo_dato else fecha_inicio_batch_colombia
            cambio_de_dia = fecha_inicio_batch_colombia != fecha_ultimo_dato_colombia
            
            # Solo cerrar el batch si:
            # 1. El flujo está en cero (mass_rate <= 0), O
            # 2. Hay cambio de día (medianoche) para reportar lo del día anterior
            if ultimo_mass_rate_kg_min <= 0 or cambio_de_dia:
                # Cálculos de masa
                masa_inicial_lb = primer_dato.total_mass
                masa_final_lb = ultimo_dato_con_flujo.total_mass
                diferencia_masa_lb = masa_final_lb - masa_inicial_lb
                diferencia_masa_kg = lb_a_kg(diferencia_masa_lb)
                
                # Cálculos de volumen (convertir de cm³ a galones)
                volumen_inicial_cm3 = primer_dato.total_volume
                volumen_final_cm3 = ultimo_dato_con_flujo.total_volume
                diferencia_volumen_cm3 = volumen_final_cm3 - volumen_inicial_cm3
                diferencia_volumen_gal = cm3_a_gal(diferencia_volumen_cm3)
                
                razon_cierre = "cambio de día (medianoche)" if cambio_de_dia else "flujo en cero al final del rango"
                logger.info(f"📦 Cerrando batch final por {razon_cierre}")
                logger.debug(f"Masa inicial (punto en 0): {masa_inicial_lb:.2f} lb en {primer_dato.created_at_iot}")
                logger.debug(f"Masa final (último punto >0): {masa_final_lb:.2f} lb en {ultimo_dato_con_flujo.created_at_iot}")
                logger.debug(f"Diferencia masa: {diferencia_masa_lb:.2f} lb = {diferencia_masa_kg:.2f} kg")
                logger.debug(f"Volumen inicial: {volumen_inicial_cm3:.2f} cm³, Volumen final: {volumen_final_cm3:.2f} cm³")
                logger.debug(f"Diferencia volumen: {diferencia_volumen_cm3:.2f} cm³ = {diferencia_volumen_gal:.3f} gal")
                
                if diferencia_masa_kg >= vol_minimo_batch:
                    temperaturas = [d.coriolis_temperature for d in datos_batch if d.coriolis_temperature is not None]
                    densidades = [d.density for d in datos_batch if d.density is not None]
                    presiones = [d.pressure_out for d in datos_batch if d.pressure_out is not None]
                    temp_prom = sum(temperaturas) / len(temperaturas) if temperaturas else 0
                    dens_prom = sum(densidades) / len(densidades) if densidades else 0
                    pres_prom = sum(presiones) / len(presiones) if presiones else None
                    
                    batches.append({
                        'fecha_inicio': primer_dato.created_at_iot,
                        'fecha_fin': ultimo_dato_con_flujo.created_at_iot,
                        'vol_total': diferencia_volumen_gal,
                        'mass_total': diferencia_masa_kg,
                        'temperatura_coriolis_prom': temp_prom,
                        'densidad_prom': dens_prom,
                        'pressure_out_prom': pres_prom,
                        'duracion_minutos': (ultimo_dato_con_flujo.created_at_iot - primer_dato.created_at_iot).total_seconds() / 60,
                        'total_registros': len(datos_batch),
                        'vol_minimo_usado': vol_minimo_batch,
                        'time_finished_usado': time_finished_batch_actual
                    })
                    logger.info(f"✅ Batch final guardado ({razon_cierre}): {primer_dato.created_at_iot} - {ultimo_dato_con_flujo.created_at_iot}, Vol: {diferencia_volumen_gal:.3f} gal, Masa: {diferencia_masa_kg:.2f} kg")
                else:
                    logger.info(f"❌ Batch final descartado: {diferencia_masa_kg:.2f} kg < {vol_minimo_batch} kg")
            else:
                logger.info(f"⚠️ Batch NO cerrado: flujo activo ({ultimo_mass_rate_kg_min:.2f} kg/min) y sin cambio de día")
                logger.info(f"   📊 Batch aún EN PROCESO - No se generará hasta que el flujo caiga a cero o cambie de día")
                logger.info(f"   Inicio: {primer_dato.created_at_iot}, Último dato con flujo: {ultimo_dato_con_flujo.created_at_iot}")
                logger.info(f"   Total registros hasta ahora: {len(datos_batch)}")

        logger.info(f"✅ Detección completada con lógica de PERFIL DINÁMICO. {len(batches)} batches detectados")
        return batches
    
    def _generar_hash_batch(self, fecha_inicio, fecha_fin, sistema_id, vol_minimo, time_finished_batch):
        """
        Genera un hash único basado en las fechas, sistema ID, vol_minimo y time_finished_batch.
        Esto previene duplicados cuando se ejecuta la detección múltiples veces.
        Incluye parámetros que realmente afectan la detección de batches.
        """
        # Crear string único con parámetros del batch
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
        
        datos_hash = f"{sistema_id}_{fecha_inicio_str}_{fecha_fin_str}_{vol_minimo}_{time_finished_batch}"
        
        # Generar hash SHA-256
        hash_obj = hashlib.sha256(datos_hash.encode('utf-8'))
        return hash_obj.hexdigest()