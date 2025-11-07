import logging
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes
from _AppMonitoreoCoriolis.models import BatchDetectado
from _AppAdmin.mixins import ComplementosPermissionMixin

# Configurar logging
logger = logging.getLogger(__name__)

class ActualizarConfiguracionCommandView(ComplementosPermissionMixin,APIView):
    """
    CBV para actualizar la configuración de coeficientes de un sistema
    Incluye validación de número de ticket
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, sistema_id):
        try:
            # Validar que el sistema existe
            sistema = get_object_or_404(Sistema, id=sistema_id)
            
            # Obtener o crear configuración
            config, created = ConfiguracionCoeficientes.objects.get_or_create(
                systemId=sistema,
                defaults={
                    'mt': 1.0, 'bt': 0.0, 'mp': 1.0, 'bp': 0.0,
                    'zero_presion': 0.0, 'span_presion': 1.0,
                    'lim_inf_caudal_masico': 0.0, 'lim_sup_caudal_masico': 1000000.0,
                    'vol_masico_ini_batch': 0.0, 'num_ticket': 1, 'time_finished_batch': 2.0
                }
            )
            
            # Obtener datos del request
            data = request.data
            
            # Validar número de ticket si se está actualizando
            if 'num_ticket' in data:
                nuevo_num_ticket = int(data['num_ticket'])
                if not self._validar_num_ticket(sistema, nuevo_num_ticket):
                    max_ticket = BatchDetectado.objects.filter(
                        systemId=sistema, 
                        num_ticket__isnull=False
                    ).aggregate(models.Max('num_ticket'))['num_ticket__max'] or 0
                    
                    return Response({
                        'success': False,
                        'error': f'El número de ticket debe ser mayor o igual a {max_ticket + 1}, ya que el máximo ({max_ticket}) ya fue asignado.'
                    }, status=400)
            
            campos_float = [
                'mt', 'bt', 'mp', 'bp', 'zero_presion', 'span_presion',
                'lim_inf_caudal_masico', 'lim_sup_caudal_masico',
                'vol_masico_ini_batch', 'time_finished_batch',
                'mf', 'vis', 'deltavis', 'dn', 'ucal_dens', 'kcal_dens',
                'desv_dens', 'ucal_met', 'kcal_met', 'esis_met', 'ucarta_met',
                'zero_stab',
                'diagnostic_glp_density_ref', 'diagnostic_glp_density_tolerance_pct',
                'diagnostic_driver_amp_base', 'diagnostic_driver_amp_multiplier',
                'diagnostic_n1_threshold', 'diagnostic_n2_threshold',
                'diagnostic_amp_imbalance_threshold_pct'
            ]

            for campo in campos_float:
                if campo in data and data[campo] is not None and data[campo] != '':
                    try:
                        setattr(config, campo, float(data[campo]))
                    except (ValueError, TypeError):
                        logger.warning("Valor inválido para %s: %s", campo, data[campo])
                        continue

            if 'num_ticket' in data and data['num_ticket'] is not None:
                config.num_ticket = int(data['num_ticket'])

            # Campos texto
            if 'tipdens' in data:
                config.tipdens = data['tipdens'] or None

            config.save()
            
            logger.info(f"Configuración actualizada para sistema {sistema_id}")
            
            return Response({
                'success': True,
                'message': 'Configuración actualizada exitosamente',
                'configuracion': {
                    'mt': config.mt,
                    'bt': config.bt,
                    'mp': config.mp,
                    'bp': config.bp,
                    'zero_presion': config.zero_presion,
                    'span_presion': config.span_presion,
                    'lim_inf_caudal_masico': config.lim_inf_caudal_masico,
                    'lim_sup_caudal_masico': config.lim_sup_caudal_masico,
                    'vol_masico_ini_batch': config.vol_masico_ini_batch,
                    'num_ticket': config.num_ticket,
                    'time_finished_batch': config.time_finished_batch,
                    'mf': config.mf,
                    'vis': config.vis,
                    'deltavis': config.deltavis,
                    'dn': config.dn,
                    'ucal_dens': config.ucal_dens,
                    'kcal_dens': config.kcal_dens,
                    'tipdens': config.tipdens,
                    'desv_dens': config.desv_dens,
                    'ucal_met': config.ucal_met,
                    'kcal_met': config.kcal_met,
                    'esis_met': config.esis_met,
                    'ucarta_met': config.ucarta_met,
                    'zero_stab': config.zero_stab,
                    'diagnostic_glp_density_ref': config.diagnostic_glp_density_ref,
                    'diagnostic_glp_density_tolerance_pct': config.diagnostic_glp_density_tolerance_pct,
                    'diagnostic_driver_amp_base': config.diagnostic_driver_amp_base,
                    'diagnostic_driver_amp_multiplier': config.diagnostic_driver_amp_multiplier,
                    'diagnostic_n1_threshold': config.diagnostic_n1_threshold,
                    'diagnostic_n2_threshold': config.diagnostic_n2_threshold,
                    'diagnostic_amp_imbalance_threshold_pct': config.diagnostic_amp_imbalance_threshold_pct
                }
            })
            
        except Exception as e:
            logger.error(f"Error actualizando configuración: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
    
    def _validar_num_ticket(self, sistema, nuevo_num_ticket):
        """
        Valida que el nuevo número de ticket sea mayor o igual al máximo + 1
        """
        max_ticket = BatchDetectado.objects.filter(
            systemId=sistema,
            num_ticket__isnull=False
        ).aggregate(models.Max('num_ticket'))['num_ticket__max'] or 0
        
        return nuevo_num_ticket >= (max_ticket + 1)
