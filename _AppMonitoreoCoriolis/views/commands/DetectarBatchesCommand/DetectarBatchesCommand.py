import logging
import hashlib
from datetime import datetime
from django.utils import timezone as django_timezone
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes
from _AppMonitoreoCoriolis.models import NodeRedData, BatchDetectado
from UTIL_LIB.conversiones import lb_s_a_kg_min, lb_a_kg
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
            
            # Convertir fechas a datetime
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Convertir a timezone aware
            fecha_inicio = django_timezone.make_aware(fecha_inicio)
            fecha_fin = django_timezone.make_aware(fecha_fin)
            
            # Obtener datos del rango de fechas, ordenados por fecha
            datos = NodeRedData.objects.filter(
                systemId=sistema,
                created_at__gte=fecha_inicio,
                created_at__lte=fecha_fin
            ).order_by('created_at')
            
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
                    lim_inf, 
                    lim_sup, 
                    vol_minimo
                )
                
                try:
                    # Intentar crear el batch con el hash único
                    batch = BatchDetectado.objects.create(
                        systemId=sistema,
                        fecha_inicio=batch_data['fecha_inicio'],
                        fecha_fin=batch_data['fecha_fin'],
                        vol_total=batch_data['vol_total'],
                        temperatura_coriolis_prom=batch_data['temperatura_coriolis_prom'],
                        densidad_prom=batch_data['densidad_prom'],
                        hash_identificacion=hash_batch,
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
                    'temperatura_coriolis_prom': round(batch.temperatura_coriolis_prom, 2),
                    'densidad_prom': round(batch.densidad_prom, 4),
                    'duracion_minutos': round(batch.duracion_minutos, 2),
                    'total_registros': batch.total_registros
                })
            
            return Response({
                'success': True,
                'batches_detectados': len(batches_guardados),
                'batches_nuevos': len(batches_guardados) - batches_existentes,
                'batches_existentes': batches_existentes,
                'batches': batches_guardados,
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
        Algoritmo para detectar batches basado en la nueva lógica de estados
        
        Args:
            datos: QuerySet de NodeRedData ordenado por created_at
            lim_inf: Límite inferior de caudal másico (kg/min)
            lim_sup: Límite superior de caudal másico (kg/min)
            vol_minimo: Volumen mínimo para considerar un batch válido (kg)
            
        Lógica de detección por estados:
        1. Cuando flujo > LimInf: Inicia totalización (fase fantasma)
        2. Si masa acumulada >= vol_minimo Y flujo > LimSup: Confirma batch estable
        3. Cuando flujo < LimInf: Finaliza batch (si estaba confirmado) o descarta (si era fantasma)
        
        Nota: Los datos de mass_rate en la DB están en lb/sec y se convierten 
              automáticamente a kg/min para comparar con los límites.
        """
        batches = []
        
        # Estados del algoritmo
        estado = "sin_batch"  # Posibles estados: "sin_batch", "totalizando_fantasma", "batch_confirmado"
        inicio_totalizacion = None
        masa_inicial_totalizacion = None
        datos_totalizacion = []
        batch_confirmado_en = None
        
        logger.info(f"Iniciando detección de batches con nueva lógica. Límites: inf={lim_inf}, sup={lim_sup}, vol_min={vol_minimo}")
        
        for i, dato in enumerate(datos):
            mass_rate_raw = dato.mass_rate  # En lb/sec
            total_mass = dato.total_mass
            
            # Verificar que tenemos los datos necesarios
            if mass_rate_raw is None or total_mass is None:
                continue
            
            # Convertir mass_rate de lb/sec a kg/min para comparar con los límites
            mass_rate_kg_min = lb_s_a_kg_min(mass_rate_raw)
            
            # Calcular masa acumulada si estamos totalizando (convertir de lb a kg)
            masa_acumulada_kg = 0
            if masa_inicial_totalizacion is not None:
                masa_acumulada_lb = total_mass - masa_inicial_totalizacion
                masa_acumulada_kg = lb_a_kg(masa_acumulada_lb)
            
            # MÁQUINA DE ESTADOS PARA DETECCIÓN DE BATCH
            
            if estado == "sin_batch":
                # 1. INICIO DE TOTALIZACIÓN: Cuando el flujo másico supera el LimInf
                if mass_rate_kg_min > lim_inf:
                    estado = "totalizando_fantasma"
                    inicio_totalizacion = dato.created_at
                    masa_inicial_totalizacion = total_mass  # En lb
                    datos_totalizacion = [dato]
                    logger.debug(f"Iniciando totalización fantasma en {inicio_totalizacion}, flujo: {mass_rate_kg_min:.2f} kg/min")
                    
            elif estado == "totalizando_fantasma":
                if mass_rate_kg_min > lim_inf:
                    # Seguimos totalizando
                    datos_totalizacion.append(dato)
                    
                    # 2. VALIDACIÓN DEL BATCH: Verificar si alcanzamos el volumen mínimo
                    if masa_acumulada_kg >= vol_minimo:
                        # Verificar si ya superamos LimSup para confirmar batch estable
                        if mass_rate_kg_min > lim_sup:
                            # 3. CONFIRMACIÓN DE BATCH ESTABLE
                            estado = "batch_confirmado"
                            batch_confirmado_en = dato.created_at
                            logger.debug(f"Batch confirmado como estable en {batch_confirmado_en}, masa acumulada: {masa_acumulada_kg:.2f} kg")
                        # Si no supera LimSup, seguimos en fase fantasma pero con volumen suficiente
                        
                else:
                    # 4. REINGRESO O CAÍDA DE FLUJO: El flujo bajó del LimInf antes de confirmar batch
                    logger.debug(f"Flujo bajo del LimInf antes de confirmar batch. Descartando masa fantasma: {masa_acumulada_kg:.2f} kg")
                    estado = "sin_batch"
                    inicio_totalizacion = None
                    masa_inicial_totalizacion = None
                    datos_totalizacion = []
                    batch_confirmado_en = None
                    
            elif estado == "batch_confirmado":
                if mass_rate_kg_min > lim_inf:
                    # Seguimos totalizando en batch confirmado
                    datos_totalizacion.append(dato)
                    
                    # Verificar si supera LimSup (por si no lo había hecho antes)
                    if mass_rate_kg_min > lim_sup and batch_confirmado_en is None:
                        batch_confirmado_en = dato.created_at
                        
                else:
                    # El flujo cayó por debajo de LimInf: FINALIZAR BATCH CONFIRMADO
                    fin_batch = dato.created_at
                    masa_final = total_mass
                    masa_total_batch_lb = masa_final - masa_inicial_totalizacion
                    masa_total_batch_kg = lb_a_kg(masa_total_batch_lb)
                    
                    logger.debug(f"Finalizando batch confirmado. Masa total: {masa_total_batch_kg:.2f} kg")
                    
                    # Calcular promedios
                    if datos_totalizacion:
                        temperaturas = [d.coriolis_temperature for d in datos_totalizacion if d.coriolis_temperature is not None]
                        densidades = [d.density for d in datos_totalizacion if d.density is not None]
                        
                        if temperaturas and densidades:
                            temp_prom = sum(temperaturas) / len(temperaturas)
                            dens_prom = sum(densidades) / len(densidades)
                            
                            # Guardar batch detectado
                            batches.append({
                                'fecha_inicio': inicio_totalizacion,
                                'fecha_fin': fin_batch,
                                'vol_total': masa_total_batch_kg,  # En kg
                                'temperatura_coriolis_prom': temp_prom,
                                'densidad_prom': dens_prom,
                                'duracion_minutos': (fin_batch - inicio_totalizacion).total_seconds() / 60,
                                'total_registros': len(datos_totalizacion)
                            })
                            
                            logger.info(f"Batch guardado: {inicio_totalizacion} - {fin_batch}, {masa_total_batch_kg:.2f} kg")
                    
                    # Resetear estado
                    estado = "sin_batch"
                    inicio_totalizacion = None
                    masa_inicial_totalizacion = None
                    datos_totalizacion = []
                    batch_confirmado_en = None
        
        # Si terminamos con un batch confirmado en progreso, finalizarlo
        if estado == "batch_confirmado" and datos_totalizacion and masa_inicial_totalizacion is not None:
            ultimo_dato = datos_totalizacion[-1]
            masa_total_batch_lb = ultimo_dato.total_mass - masa_inicial_totalizacion
            masa_total_batch_kg = lb_a_kg(masa_total_batch_lb)
            
            if masa_total_batch_kg >= vol_minimo:
                temperaturas = [d.coriolis_temperature for d in datos_totalizacion if d.coriolis_temperature is not None]
                densidades = [d.density for d in datos_totalizacion if d.density is not None]
                
                if temperaturas and densidades:
                    temp_prom = sum(temperaturas) / len(temperaturas)
                    dens_prom = sum(densidades) / len(densidades)
                    
                    batches.append({
                        'fecha_inicio': inicio_totalizacion,
                        'fecha_fin': ultimo_dato.created_at,
                        'vol_total': masa_total_batch_kg,  # En kg
                        'temperatura_coriolis_prom': temp_prom,
                        'densidad_prom': dens_prom,
                        'duracion_minutos': (ultimo_dato.created_at - inicio_totalizacion).total_seconds() / 60,
                        'total_registros': len(datos_totalizacion)
                    })
        
        logger.info(f"Detección completada con nueva lógica. {len(batches)} batches detectados")
        return batches
    
    def _generar_hash_batch(self, fecha_inicio, fecha_fin, sistema_id, lim_inf, lim_sup, vol_minimo):
        """
        Genera un hash único basado en las fechas, sistema ID y configuración.
        Esto previene duplicados cuando se ejecuta la detección múltiples veces.
        """
        # Crear string único con parámetros del batch
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
        
        datos_hash = f"{sistema_id}_{fecha_inicio_str}_{fecha_fin_str}_{lim_inf}_{lim_sup}_{vol_minimo}"
        
        # Generar hash SHA-256
        hash_obj = hashlib.sha256(datos_hash.encode('utf-8'))
        return hash_obj.hexdigest()