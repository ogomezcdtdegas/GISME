"""
Context processors para hacer disponibles variables de usuario en todos los templates
"""

def user_role_context(request):
    """
    Context processor para hacer disponible el rol del usuario en todos los templates
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        user_role = None
        if hasattr(request.user, 'user_role') and request.user.user_role:
            user_role = request.user.user_role.role
        
        return {
            'current_user_role': user_role,
            'can_access_admin': user_role in ['admin', 'admin_principal'],
            'can_create_users': user_role == 'admin_principal',
            'can_edit_users': user_role == 'admin_principal',
            'can_delete_users': user_role == 'admin_principal',
            'is_supervisor': user_role == 'supervisor',
            'is_admin': user_role == 'admin',
            'is_admin_principal': user_role == 'admin_principal',
            'is_superuser': request.user.is_superuser,
            'can_delete_records': request.user.is_superuser,
        }
    
    return {
        'current_user_role': None,
        'can_access_admin': False,
        'can_create_users': False,
        'can_edit_users': False,
        'can_delete_users': False,
        'is_supervisor': False,
        'is_admin': False,
        'is_admin_principal': False,
        'is_superuser': False,
        'can_delete_records': False,
    }