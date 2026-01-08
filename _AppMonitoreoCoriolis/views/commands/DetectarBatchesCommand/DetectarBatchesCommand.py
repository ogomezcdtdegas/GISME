import logging
import hashlib
import pytz
from datetime import datetime, time, timedelta
from django.utils import timezone as django_timezone
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes
from _AppMonitoreoCoriolis.models import NodeRedData, BatchDetectado
from UTIL_LIB.conversiones import lb_s_a_kg_min, lb_a_kg, cm3_a_gal
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ

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
            margen_deteccion = timedelta(hours=2)  # 2 horas después de fecha_fin
            fecha_fin_con_margen = fecha_fin + margen_deteccion
            
            logger.info(f"Detectando batches - Rango: {fecha_inicio_colombia.strftime('%d/%m/%Y %H:%M')} a {fecha_fin_colombia.strftime('%d/%m/%Y %H:%M')} (Colombia)")
            
            # Obtener datos del rango de fechas CON MARGEN, ordenados por fecha IoT
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at_iot__gte=fecha_inicio,
                created_at_iot__lte=fecha_fin_con_margen,  # Usar fecha con margen
                created_at_iot__isnull=False  # Solo datos con timestamp IoT válido
            ).order_by('created_at_iot')
            
            if not datos.exists():
                return Response({
                    'success': False,
                    'error': 'No se encontraron datos en el rango de fechas especificado'
                }, status=404)
            
            # Ejecutar algoritmo de detección de batches con perfil dinámico
            # Pasar fecha_inicio y fecha_fin (sin margen) para validar el rango en la detección
            batches_detectados = self._detectar_batches_con_perfil_dinamico(
                datos, lim_inf, lim_sup, sistema, fecha_inicio, fecha_fin
            )
            
            # FILTRAR batches detectados: solo guardar los que INICIAN dentro del rango solicitado
            # Esto evita que se guarden batches del día siguiente cuando se usa margen de detección
            batches_en_rango = []
            batches_fuera_rango = 0
            for batch_data in batches_detectados:
                fecha_inicio_batch = batch_data['fecha_inicio']
                if fecha_inicio <= fecha_inicio_batch <= fecha_fin:
                    batches_en_rango.append(batch_data)
                else:
                    batches_fuera_rango += 1
            
            if batches_fuera_rango > 0:
                logger.info(f"Filtrados {batches_fuera_rango} batches fuera del rango solicitado")
            
            # Calcular masa total bruta del rango (sin perfil, solo mass_rate > 0)
            masa_total_bruta_kg = self._calcular_masa_total_bruta(datos, fecha_inicio, fecha_fin)
            
            # Guardar batches en la base de datos con prevención de duplicados
            batches_guardados = []
            batches_existentes = 0
            batches_nuevos = 0
            
            for batch_data in batches_en_rango:
                # Generar hash para este batch usando el perfil dinámico que se usó
                hash_batch = self._generar_hash_batch(
                    batch_data['fecha_inicio'],
                    batch_data['fecha_fin'], 
                    sistema_id,
                    batch_data['vol_minimo_usado'],
                    batch_data['time_finished_usado']
                )
                
                # VERIFICAR PRIMERO SI YA EXISTE antes de intentar crear
                batch_existente = BatchDetectado.objects.filter(hash_identificacion=hash_batch).first()
                
                if batch_existente:
                    # El batch ya existe, no crear duplicado
                    batches_existentes += 1
                    batch = batch_existente
                else:
                    # El batch NO existe, crear uno nuevo
                    try:
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
                        batches_nuevos += 1
                    except IntegrityError:
                        # Condición de carrera: otro proceso creó el batch
                        batch = BatchDetectado.objects.get(hash_identificacion=hash_batch)
                        batches_existentes += 1
                
                # Agregar a la lista de respuesta (ya sea nuevo o existente)
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
            # IMPORTANTE: Filtrar por fecha_inicio dentro del rango solicitado
            # Esto asegura que solo se retornen batches del día o días solicitados
            todos_batches = BatchDetectado.objects.filter(
                systemId=sistema,
                fecha_inicio__gte=fecha_inicio,
                fecha_inicio__lte=fecha_fin  # Cambiar de fecha_fin__lte a fecha_inicio__lte
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
            
            logger.info(f"✅ Proceso completado: {batches_nuevos} nuevos, {batches_existentes} existentes, {len(batches_completos)} total")
            
            return Response({
                'success': True,
                'batches_detectados': len(batches_completos),
                'batches_nuevos': batches_nuevos,
                'batches_existentes': batches_existentes,
                'batches': batches_completos,
                'masa_total_bruta_kg': round(masa_total_bruta_kg, 2),
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
    
    def _detectar_batches_con_perfil_dinamico(self, datos, lim_inf, lim_sup, sistema, fecha_inicio_rango, fecha_fin_rango):
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
            fecha_inicio_rango: Datetime de inicio del rango solicitado (UTC, sin margen)
            fecha_fin_rango: Datetime de fin del rango solicitado (UTC, sin margen)
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
                                    'fecha_fin': fecha_fin_dia_anterior,  # Usar 23:59:59.999999 del día anterior
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
                        logger.info(f"� Flujo volvió a subir después de {minutos_antes_subir:.2f} min - Continuando batch")
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
                            # 🔄 Resetear perfil para el siguiente batch
                            vol_minimo_batch = None
                            time_finished_batch_actual = None
                        # Si no ha pasado el tiempo, seguir esperando (sin log)
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
    
    def _calcular_masa_total_bruta(self, datos, fecha_inicio, fecha_fin):
        """
        Calcula la masa total bruta del rango SIN considerar perfil de detección.
        Solo cuenta cuando hay flujo (mass_rate > 0) y detecta resets automáticamente.
        
        Args:
            datos: QuerySet de NodeRedData ordenado por created_at_iot
            fecha_inicio: Datetime de inicio del rango en UTC
            fecha_fin: Datetime de fin del rango en UTC
            
        Returns:
            float: Masa total acumulada en kg
        """
        masa_total_acumulada = 0.0
        masa_anterior = None
        registros_procesados = 0
        resets_detectados = 0
        
        for dato in datos:
            # Filtrar solo datos dentro del rango exacto (sin margen)
            if not (fecha_inicio <= dato.created_at_iot <= fecha_fin):
                continue
                
            mass_rate_raw = dato.mass_rate
            total_mass_actual = dato.total_mass
            
            # Solo procesar si hay datos válidos
            if mass_rate_raw is None or total_mass_actual is None:
                continue
            
            registros_procesados += 1
            
            # Convertir a kg/min para verificar si hay flujo
            mass_rate_kg_min = lb_s_a_kg_min(mass_rate_raw)
            
            # Solo contar masa cuando HAY FLUJO (mass_rate > 0)
            if mass_rate_kg_min > 0:
                if masa_anterior is not None:
                    diferencia = total_mass_actual - masa_anterior
                    
                    # Detección de reset: Si la diferencia es negativa o muy grande
                    if diferencia < 0 or diferencia > 100000:  # 100,000 lb como límite razonable
                        # Hubo reset, reiniciar desde el valor actual
                        resets_detectados += 1
                        logger.info(f"🔄 Reset #{resets_detectados} detectado en masa bruta: {masa_anterior:.2f} -> {total_mass_actual:.2f} lb en {dato.created_at_iot.astimezone(COLOMBIA_TZ)}")
                        masa_anterior = total_mass_actual
                    else:
                        # Acumulación normal
                        masa_acumulada_lb = diferencia
                        masa_acumulada_kg = lb_a_kg(masa_acumulada_lb)
                        masa_total_acumulada += masa_acumulada_kg
                        masa_anterior = total_mass_actual
                else:
                    # Primera lectura con flujo
                    logger.info(f"🟢 Primera lectura con flujo: total_mass = {total_mass_actual:.2f} lb, mass_rate = {mass_rate_kg_min:.2f} kg/min")
                    masa_anterior = total_mass_actual
            # Si mass_rate <= 0, mantener última referencia (no actualizar masa_anterior)
        
        if resets_detectados > 0:
            logger.info(f"Masa total: {masa_total_acumulada:.2f} kg - {resets_detectados} resets detectados")
        
        return masa_total_acumulada