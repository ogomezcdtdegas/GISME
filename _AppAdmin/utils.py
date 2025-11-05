"""
Utilidades para el logging de acciones de usuarios
"""
from _AppAdmin.models import UserActionLog


def log_user_action(user, action, affected_type, affected_value, affected_id, ip_address=None):
    """
    Registrar una acción del usuario en el sistema
    
    Args:
        user: Usuario que realizó la acción
        action: Acción realizada ('crear', 'editar', 'inactivar', 'activar')
        affected_type: Tipo de registro afectado ('ubicacion', 'sistema', 'usuario')
        affected_value: Valor string del registro afectado (ej: nombre de la ubicación)
        affected_id: ID del registro afectado
        ip_address: Dirección IP del usuario (opcional)
    """
    try:
        log_entry = UserActionLog.objects.create(
            user=user,
            email=user.email if user else '',
            action=action,
            affected_type=affected_type,
            affected_value=str(affected_value),
            affected_id=affected_id,
            ip_address=ip_address or ''
        )
    except Exception as e:
        # En caso de error, solo registrar en logs pero no interrumpir el flujo
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al registrar acción del usuario: {e}", exc_info=True)


def get_client_ip(request):
    """
    Obtener la dirección IP del cliente desde el request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip