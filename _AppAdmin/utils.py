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
        affected_type: Tipo de registro afectado ('ubicacion', 'sistema')
        affected_value: Valor string del registro afectado (ej: nombre de la ubicación)
        affected_id: ID del registro afectado
        ip_address: Dirección IP del usuario (opcional)
    """
    print(f"DEBUG LOG_USER_ACTION: Llamada con parametros:")
    print(f"  user: {user}")
    print(f"  action: {action}")
    print(f"  affected_type: {affected_type}")
    print(f"  affected_value: {affected_value}")
    print(f"  affected_id: {affected_id}")
    print(f"  ip_address: {ip_address}")
    
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
        print(f"DEBUG LOG_USER_ACTION: Log creado exitosamente con ID: {log_entry.id}")
    except Exception as e:
        # En caso de error, solo registrar en logs pero no interrumpir el flujo
        print(f"Error al registrar acción del usuario: {e}")
        import traceback
        traceback.print_exc()


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