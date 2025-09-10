from django.db import models
from django.contrib.auth.models import User

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
