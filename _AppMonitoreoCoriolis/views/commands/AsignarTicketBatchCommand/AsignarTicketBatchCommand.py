import logging
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from _AppComplementos.models import ConfiguracionCoeficientes
from _AppMonitoreoCoriolis.models import BatchDetectado
from _AppAdmin.mixins import ComplementosPermissionMixin

# Configurar logging
logger = logging.getLogger(__name__)

class AsignarTicketBatchCommandView(ComplementosPermissionMixin,APIView):
    """
    CBV Command para asignar un ticket a un batch específico
    Toma el número actual de ticket de configuración, lo asigna al batch
    e incrementa en 1 el número de ticket en configuración
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, batch_id):
        try:
            # Obtener el batch
            batch = get_object_or_404(BatchDetectado, id=batch_id)
            
            # Verificar que el batch no tiene ticket ya asignado
            if batch.num_ticket is not None:
                return Response({
                    'success': False,
                    'error': f'Este batch ya tiene asignado el ticket #{batch.num_ticket}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener la configuración del sistema
            try:
                config = ConfiguracionCoeficientes.objects.get(systemId=batch.systemId)
            except ConfiguracionCoeficientes.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'No se encontró configuración de coeficientes para este sistema'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Asignar el ticket actual al batch
            ticket_asignado = config.num_ticket
            batch.num_ticket = ticket_asignado
            batch.save()
            
            # Incrementar el número de ticket en configuración
            config.num_ticket += 1
            config.save()
            
            logger.info(f"Ticket #{ticket_asignado} asignado al batch {batch.id}. Nuevo ticket disponible: {config.num_ticket}")
            
            return Response({
                'success': True,
                'message': f'Ticket #{ticket_asignado} asignado exitosamente',
                'data': {
                    'batch_id': str(batch.id),
                    'ticket_asignado': ticket_asignado,
                    'nuevo_ticket_disponible': config.num_ticket,
                    'sistema': {
                        'id': str(batch.systemId.id),
                        'tag': batch.systemId.tag,
                        'sistema_id': batch.systemId.sistema_id
                    },
                    'batch_info': {
                        'fecha_inicio': batch.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S'),
                        'fecha_fin': batch.fecha_fin.strftime('%Y-%m-%d %H:%M:%S'),
                        'vol_total': batch.vol_total
                    }
                }
            })
            
        except Exception as e:
            logger.error(f"Error asignando ticket al batch {batch_id}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)