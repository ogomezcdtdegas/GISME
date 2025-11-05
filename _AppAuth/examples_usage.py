"""
Ejemplo de cómo usar los mixins y helpers centralizados de _AppAuth
en cualquier otra app del proyecto
"""

"""

# EJEMPLO 1: Usando el helper get_user_role_context
from _AppAuth.utils import get_user_role_context

class MiVistaEjemplo(LoginRequiredMixin, TemplateView):
    template_name = 'mi_app/mi_template.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar contexto de rol - UNA SOLA LÍNEA
        context.update(get_user_role_context(self.request.user))
        
        return context


# EJEMPLO 2: Usando UserRoleContextMixin
from _AppAuth.utils import UserRoleContextMixin

class MiVistaConMixin(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    template_name = 'mi_app/mi_template.html'
    
    # El contexto de rol se agrega automáticamente
    # No necesitas override get_context_data


# EJEMPLO 3: Usando RoleRequiredMixin para proteger vistas
from _AppAuth.utils import RoleRequiredMixin

class VistaProtegida(RoleRequiredMixin, TemplateView):
    template_name = 'mi_app/solo_admin.html'
    required_roles = ['admin', 'admin_principal']  # Solo admin pueden acceder

"""

# EJEMPLO 4: En tus templates HTML
"""
<!-- En cualquier template.html -->
{% if can_create_users %}
    <button class="btn btn-success">Crear Usuario</button>
{% endif %}

{% if can_edit_users %}
    <a href="{% url 'editar' %}" class="btn btn-primary">Editar</a>
{% else %}
    <button class="btn btn-secondary" disabled title="Sin permisos">Editar</button>
{% endif %}

{% if is_supervisor %}
    <div class="alert alert-info">Acceso limitado para Supervisores</div>
{% endif %}

{% if access_denied %}
    <div class="alert alert-danger">{{ access_denied_message }}</div>
{% endif %}

<!-- Mostrar información del rol actual -->
<span class="badge badge-info">Rol: {{ current_user_role|title }}</span>
"""
