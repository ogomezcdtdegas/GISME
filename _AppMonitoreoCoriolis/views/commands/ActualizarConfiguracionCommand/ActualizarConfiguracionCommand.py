import logging
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes
from _AppMonitoreoCoriolis.models import BatchDetectado

# Configurar logging
logger = logging.getLogger(__name__)

class ActualizarConfiguracionCommandView(APIView):
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
                    'vol_masico_ini_batch': 0.0, 'num_ticket': 1
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
            
            # Actualizar campos
            campos_actualizables = [
                'mt', 'bt', 'mp', 'bp', 'zero_presion', 'span_presion',
                'lim_inf_caudal_masico', 'lim_sup_caudal_masico', 
                'vol_masico_ini_batch', 'num_ticket'
            ]
            
            for campo in campos_actualizables:
                if campo in data:
                    setattr(config, campo, data[campo])
            
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
                    'num_ticket': config.num_ticket
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