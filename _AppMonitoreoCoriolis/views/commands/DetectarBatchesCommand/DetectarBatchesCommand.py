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
            
            # Obtener límites de configuración
            try:
                config = ConfiguracionCoeficientes.objects.get(systemId=sistema)
                lim_inf = config.lim_inf_caudal_masico  # En kg/min
                lim_sup = config.lim_sup_caudal_masico  # En kg/min
                vol_minimo = config.vol_masico_ini_batch  # En kg - volumen mínimo para considerar batch
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
            
            # Log para debugging de zona horaria
            logger.info(f"Fechas Colombia - Inicio: {fecha_inicio_colombia} | Fin: {fecha_fin_colombia}")
            logger.info(f"Fechas UTC (para DB) - Inicio: {fecha_inicio} | Fin: {fecha_fin}")
            logger.info(f"Input recibido - fecha_inicio_str: '{fecha_inicio_str}', fecha_fin_str: '{fecha_fin_str}'")
            
            # Obtener datos del rango de fechas, ordenados por fecha IoT
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at_iot__gte=fecha_inicio,
                created_at_iot__lte=fecha_fin,
                created_at_iot__isnull=False  # Solo datos con timestamp IoT válido
            ).order_by('created_at_iot')
            
            if not datos.exists():
                return Response({
                    'success': False,
                    'error': 'No se encontraron datos en el rango de fechas especificado'
                }, status=404)
            
            # Ejecutar algoritmo de detección de batches con nueva lógica
            batches_detectados = self._detectar_batches_nueva_logica(datos, lim_inf, lim_sup, vol_minimo, sistema)
            
            # Guardar batches en la base de datos con prevención de duplicados
            batches_guardados = []
            batches_existentes = 0
            
            for batch_data in batches_detectados:
                # Generar hash para este batch
                hash_batch = self._generar_hash_batch(
                    batch_data['fecha_inicio'],
                    batch_data['fecha_fin'], 
                    sistema_id,
                    vol_minimo
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
                        perfil_vol_minimo=vol_minimo,
                        duracion_minutos=batch_data['duracion_minutos'],
                        total_registros=batch_data['total_registros']
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
                    'vol_minimo_batch': vol_minimo
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
    
    def _detectar_batches_nueva_logica(self, datos, lim_inf, lim_sup, vol_minimo, sistema):
        """
        Nueva lógica ultra-simplificada: 
        - Detecta cuando caudal cambia de 0 a > 0 (inicio de batch)
        - Detecta cuando vuelve a 0 (fin de batch)
        - Compara masa total del último punto vs primer punto
        - Si la diferencia supera vol_minimo, es batch válido
        
        Args:
            datos: QuerySet de NodeRedData ordenado por created_at_iot
            lim_inf: Límite inferior de caudal másico (kg/min) - SOLO PARA MOSTRAR
            lim_sup: Límite superior de caudal másico (kg/min) - SOLO PARA MOSTRAR
            vol_minimo: Volumen mínimo para considerar un batch válido (kg)
        """
        batches = []
        en_batch = False
        inicio_batch = None
        primer_dato = None
        datos_batch = []
        punto_anterior = None  # Para guardar el último punto donde flujo = 0

        logger.info(f"Iniciando detección con lógica de diferencia de masa total. Vol_min={vol_minimo} kg")

        for dato in datos:
            mass_rate_raw = dato.mass_rate  # En lb/sec
            total_mass = dato.total_mass
            total_volume = dato.total_volume
            
            # Verificar que tenemos los datos necesarios
            if mass_rate_raw is None or total_mass is None or total_volume is None:
                continue
                
            # Convertir mass_rate de lb/sec a kg/min
            mass_rate_kg_min = lb_s_a_kg_min(mass_rate_raw)
            
            # NUEVA LÓGICA: Detectar cambio de 0 a > 0
            if mass_rate_kg_min > 0:
                if not en_batch:
                    # Iniciar nuevo batch - usar punto anterior como referencia inicial
                    en_batch = True
                    inicio_batch = dato.created_at_iot
                    
                    # Si tenemos punto anterior (donde flujo = 0), usarlo como referencia
                    if punto_anterior is not None:
                        primer_dato = punto_anterior
                        logger.debug(f"Iniciando batch en {inicio_batch}, usando punto anterior como referencia")
                        logger.debug(f"Punto inicial (flujo=0): masa={primer_dato.total_mass} lb, volumen={primer_dato.total_volume} cm³ en {primer_dato.created_at_iot}")
                    else:
                        # Si no hay punto anterior, usar el actual
                        primer_dato = dato
                        logger.debug(f"Iniciando batch en {inicio_batch}, sin punto anterior disponible")
                    
                    datos_batch = [dato]
                    logger.debug(f"Flujo actual: {mass_rate_kg_min:.2f} kg/min, masa actual: {total_mass} lb, volumen actual: {total_volume} cm³")
                else:
                    # Continuar batch - solo agregar datos
                    datos_batch.append(dato)
            else:
                # mass_rate <= 0: terminar batch si estaba activo, o guardar como punto anterior
                if en_batch:
                    fin_batch = dato.created_at_iot
                    ultimo_dato = datos_batch[-1]  # Último punto con flujo > 0
                    
                    # Calcular diferencias de masa y volumen entre último y primer punto
                    if primer_dato and ultimo_dato:
                        # Cálculos de masa
                        masa_inicial_lb = primer_dato.total_mass
                        masa_final_lb = ultimo_dato.total_mass
                        diferencia_masa_lb = masa_final_lb - masa_inicial_lb
                        diferencia_masa_kg = lb_a_kg(diferencia_masa_lb)
                        
                        # Cálculos de volumen (convertir de cm³ a galones)
                        volumen_inicial_cm3 = primer_dato.total_volume
                        volumen_final_cm3 = ultimo_dato.total_volume
                        diferencia_volumen_cm3 = volumen_final_cm3 - volumen_inicial_cm3
                        diferencia_volumen_gal = cm3_a_gal(diferencia_volumen_cm3)
                        
                        logger.debug(f"Terminando batch en {fin_batch}")
                        logger.debug(f"Masa inicial (punto en 0): {masa_inicial_lb:.2f} lb en {primer_dato.created_at_iot}")
                        logger.debug(f"Masa final (último punto >0): {masa_final_lb:.2f} lb en {ultimo_dato.created_at_iot}")
                        logger.debug(f"Diferencia masa: {diferencia_masa_lb:.2f} lb = {diferencia_masa_kg:.2f} kg")
                        logger.debug(f"Volumen inicial: {volumen_inicial_cm3:.2f} cm³, Volumen final: {volumen_final_cm3:.2f} cm³")
                        logger.debug(f"Diferencia volumen: {diferencia_volumen_cm3:.2f} cm³ = {diferencia_volumen_gal:.3f} gal")
                        
                        # Solo guardar si la diferencia de masa supera el volumen mínimo (criterio de validación)
                        if diferencia_masa_kg >= vol_minimo:
                            # Calcular promedios
                            temperaturas = [d.coriolis_temperature for d in datos_batch if d.coriolis_temperature is not None]
                            densidades = [d.density for d in datos_batch if d.density is not None]
                            presiones = [d.pressure_out for d in datos_batch if d.pressure_out is not None]
                            temp_prom = sum(temperaturas) / len(temperaturas) if temperaturas else 0
                            dens_prom = sum(densidades) / len(densidades) if densidades else 0
                            pres_prom = sum(presiones) / len(presiones) if presiones else None
                            
                            batches.append({
                                'fecha_inicio': primer_dato.created_at_iot,  # Usar fecha IoT del punto inicial (flujo=0)
                                'fecha_fin': fin_batch,
                                'vol_total': diferencia_volumen_gal,  # Ahora almacena volumen en galones
                                'mass_total': diferencia_masa_kg,    # Ahora almacena masa en kg
                                'temperatura_coriolis_prom': temp_prom,
                                'densidad_prom': dens_prom,
                                'pressure_out_prom': pres_prom,
                                'duracion_minutos': (fin_batch - primer_dato.created_at_iot).total_seconds() / 60,
                                'total_registros': len(datos_batch)
                            })
                            logger.info(f"Batch guardado: {primer_dato.created_at_iot} - {fin_batch}, Vol: {diferencia_volumen_gal:.3f} gal, Masa: {diferencia_masa_kg:.2f} kg")
                        else:
                            logger.debug(f"Batch descartado: {diferencia_masa_kg:.2f} kg < {vol_minimo} kg")
                    
                    # Reiniciar estado
                    en_batch = False
                    inicio_batch = None
                    primer_dato = None
                    datos_batch = []
                
                # Guardar este punto como posible referencia para el próximo batch
                punto_anterior = dato

        # Si termina con un batch abierto, cerrarlo si cumple el volumen mínimo
        if en_batch and datos_batch and primer_dato is not None:
            ultimo_dato = datos_batch[-1]
            
            # Cálculos de masa
            masa_inicial_lb = primer_dato.total_mass
            masa_final_lb = ultimo_dato.total_mass
            diferencia_masa_lb = masa_final_lb - masa_inicial_lb
            diferencia_masa_kg = lb_a_kg(diferencia_masa_lb)
            
            # Cálculos de volumen (convertir de cm³ a galones)
            volumen_inicial_cm3 = primer_dato.total_volume
            volumen_final_cm3 = ultimo_dato.total_volume
            diferencia_volumen_cm3 = volumen_final_cm3 - volumen_inicial_cm3
            diferencia_volumen_gal = cm3_a_gal(diferencia_volumen_cm3)
            
            logger.debug(f"Cerrando batch abierto al final")
            logger.debug(f"Masa inicial (punto en 0): {masa_inicial_lb:.2f} lb en {primer_dato.created_at_iot}")
            logger.debug(f"Masa final (último punto >0): {masa_final_lb:.2f} lb en {ultimo_dato.created_at_iot}")
            logger.debug(f"Diferencia masa: {diferencia_masa_lb:.2f} lb = {diferencia_masa_kg:.2f} kg")
            logger.debug(f"Volumen inicial: {volumen_inicial_cm3:.2f} cm³, Volumen final: {volumen_final_cm3:.2f} cm³")
            logger.debug(f"Diferencia volumen: {diferencia_volumen_cm3:.2f} cm³ = {diferencia_volumen_gal:.3f} gal")
            
            if diferencia_masa_kg >= vol_minimo:
                temperaturas = [d.coriolis_temperature for d in datos_batch if d.coriolis_temperature is not None]
                densidades = [d.density for d in datos_batch if d.density is not None]
                presiones = [d.pressure_out for d in datos_batch if d.pressure_out is not None]
                temp_prom = sum(temperaturas) / len(temperaturas) if temperaturas else 0
                dens_prom = sum(densidades) / len(densidades) if densidades else 0
                pres_prom = sum(presiones) / len(presiones) if presiones else None
                
                batches.append({
                    'fecha_inicio': primer_dato.created_at_iot,  # Usar fecha IoT del punto inicial (flujo=0)
                    'fecha_fin': ultimo_dato.created_at_iot,
                    'vol_total': diferencia_volumen_gal,  # Ahora almacena volumen en galones
                    'mass_total': diferencia_masa_kg,    # Ahora almacena masa en kg
                    'temperatura_coriolis_prom': temp_prom,
                    'densidad_prom': dens_prom,
                    'pressure_out_prom': pres_prom,
                    'duracion_minutos': (ultimo_dato.created_at_iot - primer_dato.created_at_iot).total_seconds() / 60,
                    'total_registros': len(datos_batch)
                })
                logger.info(f"Batch final guardado: {primer_dato.created_at_iot} - {ultimo_dato.created_at_iot}, Vol: {diferencia_volumen_gal:.3f} gal, Masa: {diferencia_masa_kg:.2f} kg")

        logger.info(f"Detección completada con lógica de diferencia de masa. {len(batches)} batches detectados")
        return batches
    
    def _generar_hash_batch(self, fecha_inicio, fecha_fin, sistema_id, vol_minimo):
        """
        Genera un hash único basado en las fechas, sistema ID y vol_minimo.
        Esto previene duplicados cuando se ejecuta la detección múltiples veces.
        Solo incluye parámetros que realmente afectan la detección de batches.
        """
        # Crear string único con parámetros del batch
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
        
        datos_hash = f"{sistema_id}_{fecha_inicio_str}_{fecha_fin_str}_{vol_minimo}"
        
        # Generar hash SHA-256
        hash_obj = hashlib.sha256(datos_hash.encode('utf-8'))
        return hash_obj.hexdigest()