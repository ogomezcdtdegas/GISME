"""
Servicio de detección de batches con perfil dinámico.
Contiene el algoritmo completo de detección.
"""
import logging
import pytz
from datetime import datetime, time
from UTIL_LIB.conversiones import lb_s_a_kg_min, lb_a_kg, cm3_a_gal
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ

logger = logging.getLogger(__name__)


class BatchDetectorService:
    """
    Servicio responsable de la detección de batches con perfil dinámico.
    """
    
    def detect_batches(self, datos, lim_inf, lim_sup, sistema, fecha_inicio_rango, fecha_fin_rango):
        """
        Lógica de detección con PERFIL DINÁMICO del PRIMER DATO.
        
        Args:
            datos: QuerySet de NodeRedData ordenado por created_at_iot
            lim_inf: Límite inferior de caudal másico (kg/min) - SOLO REFERENCIA
            lim_sup: Límite superior de caudal másico (kg/min) - SOLO REFERENCIA
            sistema: Instancia del Sistema (objeto)
            fecha_inicio_rango: Datetime de inicio del rango solicitado (UTC, sin margen)
            fecha_fin_rango: Datetime de fin del rango solicitado (UTC, sin margen)
            
        Returns:
            list: Lista de diccionarios con batches detectados
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

        for dato in datos:
            mass_rate_raw = dato.mass_rate  # En lb/sec
            total_mass = dato.total_mass
            total_volume = dato.total_volume
            timestamp_actual = dato.created_at_iot
            
            # Verificar que tenemos los datos necesarios
            if mass_rate_raw is None or total_mass is None or total_volume is None:
                continue
                
            # Convertir mass_rate de lb/sec a kg/min
            mass_rate_kg_min = lb_s_a_kg_min(mass_rate_raw)
            
            # LÓGICA DINÁMICA: Detectar cambio de 0 a > 0 y manejar tiempo de espera con perfil del primer dato
            if mass_rate_kg_min > 0:
                if not en_batch:
                    # VALIDAR: NO iniciar batch si el dato está fuera del rango solicitado
                    if timestamp_actual < fecha_inicio_rango or timestamp_actual > fecha_fin_rango:
                        punto_anterior = dato
                        continue
                    
                    # Capturar perfil del primer dato
                    vol_detect = dato.vol_detect_batch
                    time_closed = dato.time_closed_batch
                    
                    # Validar que el dato tiene perfil válido
                    if vol_detect is None or time_closed is None:
                        logger.warning(f"Dato sin perfil válido (vol_detect={vol_detect}, time_closed={time_closed}) - IGNORANDO")
                        continue
                    
                    # Capturar perfil para este batch
                    vol_minimo_batch = vol_detect
                    time_finished_batch_actual = time_closed
                    
                    # Iniciar nuevo batch - usar punto anterior como referencia inicial
                    en_batch = True
                    inicio_batch = dato.created_at_iot
                    tiempo_cero_inicio = None
                    
                    logger.info(f"🆕 Batch iniciado - Perfil: vol={vol_minimo_batch:.2f}kg, time={time_finished_batch_actual:.2f}min")
                    
                    # Si tenemos punto anterior (donde flujo = 0), usarlo como referencia
                    if punto_anterior is not None:
                        primer_dato = punto_anterior
                    else:
                        primer_dato = dato
                    
                    datos_batch = [dato]
                    ultimo_dato_con_flujo = dato
                else:
                    # Continuar batch - verificar cambio de día PRIMERO antes de continuar
                    
                    # 🌙 VERIFICAR CAMBIO DE DÍA - Cerrar batch del día anterior si cruza medianoche
                    fecha_inicio_batch_colombia = primer_dato.created_at_iot.astimezone(COLOMBIA_TZ).date()
                    fecha_dato_actual_colombia = dato.created_at_iot.astimezone(COLOMBIA_TZ).date()
                    
                    if fecha_inicio_batch_colombia != fecha_dato_actual_colombia:
                        # HAY CAMBIO DE DÍA - Cerrar batch del día anterior antes de continuar
                        logger.warning(f"🌙 Cambio de día detectado: {fecha_inicio_batch_colombia} -> {fecha_dato_actual_colombia}")
                        
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
                            
                            # IMPORTANTE: Usar 23:59:59.999999 del día anterior como fecha_fin
                            fecha_fin_dia_anterior = COLOMBIA_TZ.localize(
                                datetime.combine(fecha_inicio_batch_colombia, time(23, 59, 59, 999999))
                            ).astimezone(pytz.UTC)
                            
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
                                    'fecha_fin': fecha_fin_dia_anterior,
                                    'vol_total': diferencia_volumen_gal,
                                    'mass_total': diferencia_masa_kg,
                                    'temperatura_coriolis_prom': temp_prom,
                                    'densidad_prom': dens_prom,
                                    'pressure_out_prom': pres_prom,
                                    'duracion_minutos': (fecha_fin_dia_anterior - primer_dato.created_at_iot).total_seconds() / 60,
                                    'total_registros': len(datos_dia_anterior),
                                    'vol_minimo_usado': vol_minimo_batch,
                                    'time_finished_usado': time_finished_batch_actual
                                })
                                logger.info(f"✅ Batch día anterior guardado: Masa={diferencia_masa_kg:.2f}kg, Vol={diferencia_volumen_gal:.2f}gal")
                            else:
                                logger.info(f"❌ Batch día anterior descartado: {diferencia_masa_kg:.2f}kg < {vol_minimo_batch:.2f}kg")
                        
                        # IMPORTANTE: Después de cerrar el batch del día anterior, verificar si el dato actual
                        # está dentro del rango solicitado para iniciar un nuevo batch inmediatamente
                        if timestamp_actual >= fecha_inicio_rango and timestamp_actual <= fecha_fin_rango:
                            # El dato actual está en el rango, iniciar nuevo batch con este dato
                            logger.info(f"🔄 Iniciando nuevo batch del día siguiente: {fecha_dato_actual_colombia}")
                            
                            # Capturar perfil del dato actual
                            vol_detect_nuevo = dato.vol_detect_batch
                            time_closed_nuevo = dato.time_closed_batch
                            
                            if vol_detect_nuevo is not None and time_closed_nuevo is not None:
                                # Iniciar nuevo batch con el dato actual
                                en_batch = True
                                inicio_batch = dato.created_at_iot
                                primer_dato = dato
                                datos_batch = [dato]
                                ultimo_dato_con_flujo = dato
                                tiempo_cero_inicio = None
                                vol_minimo_batch = vol_detect_nuevo
                                time_finished_batch_actual = time_closed_nuevo
                            else:
                                # Si no tiene perfil válido, reiniciar estado
                                en_batch = False
                                inicio_batch = None
                                primer_dato = None
                                datos_batch = []
                                tiempo_cero_inicio = None
                                ultimo_dato_con_flujo = None
                                vol_minimo_batch = None
                                time_finished_batch_actual = None
                        else:
                            # El dato actual está fuera del rango, reiniciar estado y no continuar
                            en_batch = False
                            inicio_batch = None
                            primer_dato = None
                            datos_batch = []
                            tiempo_cero_inicio = None
                            ultimo_dato_con_flujo = None
                            vol_minimo_batch = None
                            time_finished_batch_actual = None
                        
                        continue
                    
                    # No hay cambio de día, continuar batch normalmente
                    datos_batch.append(dato)
                    ultimo_dato_con_flujo = dato
                    
                    # Si había un contador de tiempo en cero, reiniciarlo
                    if tiempo_cero_inicio is not None:
                        tiempo_antes_subir = timestamp_actual - tiempo_cero_inicio
                        minutos_antes_subir = tiempo_antes_subir.total_seconds() / 60
                        logger.info(f"🔄 Flujo volvió a subir después de {minutos_antes_subir:.2f} min - Continuando batch")
                        tiempo_cero_inicio = None
                    else:
                        # Agregar datos al batch en curso
                        pass
            else:
                # mass_rate <= 0: verificar tiempo de espera si estaba en batch
                if en_batch:
                    if tiempo_cero_inicio is None:
                        # Primera vez que el flujo cae a cero, iniciar contador
                        tiempo_cero_inicio = timestamp_actual
                        logger.info(f"🔴 Flujo cayó a cero - Esperando {time_finished_batch_actual:.2f} min para cerrar batch")
                    else:
                        # Verificar si ya pasó el tiempo de espera
                        tiempo_transcurrido = timestamp_actual - tiempo_cero_inicio
                        minutos_en_cero = tiempo_transcurrido.total_seconds() / 60
                        
                        if minutos_en_cero >= time_finished_batch_actual:
                            # Ha pasado el tiempo de espera, cerrar el batch
                            fin_batch = tiempo_cero_inicio
                            logger.info(f"✅ Cerrando batch - {minutos_en_cero:.2f} min en cero (límite: {time_finished_batch_actual:.2f} min)")
                            
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
                                    logger.info(f"✅ Batch guardado: Vol={diferencia_volumen_gal:.2f}gal, Masa={diferencia_masa_kg:.2f}kg")
                            
                            # Reiniciar estado
                            en_batch = False
                            inicio_batch = None
                            primer_dato = None
                            datos_batch = []
                            tiempo_cero_inicio = None
                            ultimo_dato_con_flujo = None
                            vol_minimo_batch = None
                            time_finished_batch_actual = None
                        # Si no ha pasado el tiempo, seguir esperando (sin log)
                else:
                    # No hay batch activo, guardar como punto anterior
                    tiempo_cero_inicio = None
                
                # Guardar este punto como posible referencia para el próximo batch
                punto_anterior = dato

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
                logger.info(f"✅ Batch final guardado: Vol={diferencia_volumen_gal:.2f}gal, Masa={diferencia_masa_kg:.2f}kg")
            else:
                logger.info(f"❌ Batch final descartado: {diferencia_masa_kg:.2f}kg < {vol_minimo_batch:.2f}kg")
        else:
            # Batch NO cerrado: flujo activo y sin cambio de día
            pass

        logger.info(f"✅ Detección completada: {len(batches)} batches detectados")
        return batches
