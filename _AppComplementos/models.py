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
    tag = models.CharField(max_length=50, unique=True, verbose_name="Tag")
    sistema_id = models.CharField(max_length=50, unique=True, verbose_name="ID Sistema")
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='sistemas', verbose_name="Ubicación")

    class Meta:
        verbose_name = "Sistema"
        verbose_name_plural = "Sistemas"

    def __str__(self):
        return f"{self.tag} - {self.sistema_id} ({self.ubicacion.nombre})"


class ConfiguracionCoeficientes(BaseModel):
    systemId = models.ForeignKey(
        Sistema,
        on_delete=models.CASCADE,
        related_name='coeficientes',
        verbose_name="Sistema"
    )
    mt = models.FloatField(verbose_name="M Temperatura")
    bt = models.FloatField(verbose_name="B Temperatura")
    mp = models.FloatField(verbose_name="M Presión")
    bp = models.FloatField(verbose_name="B Presión")
    zero_presion = models.FloatField(verbose_name="Zero Presión", default=0.0)
    span_presion = models.FloatField(verbose_name="Span Presión", default=1.0)
    lim_inf_caudal_masico = models.FloatField(verbose_name="Límite Inferior Caudal Másico", default=0.0)
    lim_sup_caudal_masico = models.FloatField(verbose_name="Límite Superior Caudal Másico", default=1000000.0)
    vol_masico_ini_batch = models.FloatField(verbose_name="Volumen Másico Total para confirmación de bath", default=0.0)

    class Meta:
        verbose_name = "Configuración de Coeficientes"
        verbose_name_plural = "Configuraciones de Coeficientes"
        unique_together = ['systemId']  # Un sistema solo puede tener una configuración de coeficientes

    def __str__(self):
        return f"Coeficientes de {self.systemId.tag} (T: y={self.mt}x+{self.bt}, P: y={self.mp}x+{self.bp})"