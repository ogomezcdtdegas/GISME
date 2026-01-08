import logging
import pytz
from datetime import timedelta
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes
from _AppMonitoreoCoriolis.models import NodeRedData, BatchDetectado
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ

# Importar servicios y utilidades
from .services.batch_detector import BatchDetectorService
from .services.mass_calculator import MassCalculatorService
from .utils.hash_generator import generate_batch_hash
from .utils.date_handler import parse_and_validate_dates

logger = logging.getLogger(__name__)

class DetectarBatchesCommandView(APIView):
    """
    CBV para detectar batches en un rango de fechas específico
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Instanciar servicios
        self.detector = BatchDetectorService()
        self.mass_calculator = MassCalculatorService()
    
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
            dates = parse_and_validate_dates(fecha_inicio_str, fecha_fin_str)
            if 'error' in dates:
                return Response({
                    'success': False,
                    'error': dates['error']
                }, status=400)
            
            fecha_inicio = dates['fecha_inicio_utc']
            fecha_fin = dates['fecha_fin_utc']
            fecha_inicio_colombia = dates['fecha_inicio_colombia']
            fecha_fin_colombia = dates['fecha_fin_colombia']
            
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
            batches_detectados = self.detector.detect_batches(
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
            masa_total_bruta_kg = self.mass_calculator.calculate_total_mass(datos, fecha_inicio, fecha_fin)
            
            # Guardar batches en la base de datos con prevención de duplicados
            batches_guardados = []
            batches_existentes = 0
            batches_nuevos = 0
            
            for batch_data in batches_en_rango:
                # Generar hash para este batch usando el perfil dinámico que se usó
                hash_batch = generate_batch_hash(
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