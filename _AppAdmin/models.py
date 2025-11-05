from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class UserRole(models.Model):
    """Modelo para manejar roles de usuarios en la plataforma"""
    ROLES = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('admin_principal', 'AdministradorPrincipal'),
    ]
    
    # Alias para compatibilidad con el serializer
    ROLE_CHOICES = ROLES
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role')
    role = models.CharField(max_length=20, choices=ROLES, default='supervisor')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rol de Usuario'
        verbose_name_plural = 'Roles de Usuarios'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"


class UserActionLog(models.Model):
    """
    Modelo para registrar las acciones de usuarios en el sistema
    Almacena información de crear, editar e inactivar para ubicaciones y sistemas
    """
    # Campo created_at que falta
    created_at = models.DateTimeField(default=timezone.now)
    
    ACTIONS = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('inactivar', 'Inactivar'),
        ('activar', 'Activar'),
    ]
    
    AFFECTED_TYPES = [
        ('ubicacion', 'Ubicación'),
        ('sistema', 'Sistema'),
        ('usuario', 'Usuario'),  # Agregar usuario
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_logs')
    email = models.EmailField(help_text="Email del usuario que realizó la acción")
    action = models.CharField(max_length=20, choices=ACTIONS, help_text="Acción realizada")
    action_datetime = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora de la acción")
    affected_type = models.CharField(max_length=20, choices=AFFECTED_TYPES, help_text="Tipo de registro afectado")
    affected_value = models.CharField(max_length=255, help_text="Valor del registro afectado")
    affected_id = models.CharField(max_length=255, help_text="ID del registro afectado")
    ip_address = models.CharField(max_length=45, help_text="Dirección IP del usuario")

    class Meta:
        verbose_name = "Log de Acción de Usuario"
        verbose_name_plural = "Logs de Acciones de Usuarios"
        ordering = ['-action_datetime']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['action_datetime']),
            models.Index(fields=['user']),
            models.Index(fields=['affected_type']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.email} - {self.get_action_display()} {self.get_affected_type_display()}: {self.affected_value} - {self.action_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
