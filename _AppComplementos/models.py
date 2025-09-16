from django.db import models
from _AppCommon.models import BaseModel  # Importamos el modelo base


class Ubicacion(BaseModel):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Ubicación")
    latitud = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Latitud")
    longitud = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Longitud")

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"

    def __str__(self):
        return f"{self.nombre} (Lat: {self.latitud}, Lng: {self.longitud})"
    
class Sistema(BaseModel):
    tag = models.CharField(max_length=50, verbose_name="Tag")
    sistema_id = models.CharField(max_length=50, verbose_name="ID Sistema")
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='sistemas', verbose_name="Ubicación")

    class Meta:
        verbose_name = "Sistema"
        verbose_name_plural = "Sistemas"
        unique_together = ('tag', 'sistema_id', 'ubicacion')  # Evita duplicados del mismo tag, id y ubicación

    def __str__(self):
        return f"{self.tag} - {self.sistema_id} ({self.ubicacion.nombre})"