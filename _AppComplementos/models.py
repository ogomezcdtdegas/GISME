from django.db import models
from _AppCommon.models import BaseModel  # Importamos el modelo base


class Criticidad(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Criticidad"
        verbose_name_plural = "Criticidades"

    def __str__(self):
        return f"{self.name}"


class TipoCriticidad(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Tipo de Criticidad"
        verbose_name_plural = "Tipos de Criticidad"

    def __str__(self):
        return f"{self.name}"
    
class Producto(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name}"
    
class TipoCriticidadCriticidad(BaseModel):
    tipo_criticidad = models.ForeignKey(TipoCriticidad, on_delete=models.CASCADE)
    criticidad = models.ForeignKey(Criticidad, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tipo_criticidad', 'criticidad')  # Evita duplicados

    def __str__(self):
        return f"{self.tipo_criticidad.name} - {self.criticidad.name}"
    
class ProductoTipoCritCrit(BaseModel):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    relacion_tipo_criticidad = models.ForeignKey(TipoCriticidadCriticidad, on_delete=models.CASCADE)  # 🔥 Conexión directa

    class Meta:
        unique_together = ('producto', 'relacion_tipo_criticidad')  # Evita duplicados

    def __str__(self):
        relacion = self.relacion_tipo_criticidad
        return f"{self.producto.name} - {relacion.tipo_criticidad.name} ({relacion.criticidad.name})"