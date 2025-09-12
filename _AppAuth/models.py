from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserLoginLog(models.Model):
    """
    Modelo para registrar los logs de login de usuarios
    Almacena información básica de cada inicio de sesión exitoso
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs')
    email = models.EmailField(help_text="Email del usuario que hizo login")
    login_datetime = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora del login")
    ip_address = models.CharField(max_length=45, help_text="Dirección IP del usuario")

    class Meta:
        verbose_name = "Log de Login"
        verbose_name_plural = "Logs de Login"
        ordering = ['-login_datetime']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['login_datetime']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.email} - {self.login_datetime.strftime('%Y-%m-%d %H:%M:%S')} - {self.ip_address}"

# Create your models here.
