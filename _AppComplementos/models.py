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
    criticidad = models.ForeignKey(Criticidad, on_delete=models.CASCADE, related_name='tipo_criticidad_relaciones')

    class Meta:
        unique_together = ('tipo_criticidad', 'criticidad')  # Evita duplicados

    def __str__(self):
        return f"{self.tipo_criticidad.name} - {self.criticidad.name}"
    
class ProductoTipoCritCrit(BaseModel):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    relacion_tipo_criticidad = models.ForeignKey(TipoCriticidadCriticidad, on_delete=models.CASCADE, related_name='productos')

    class Meta:
        unique_together = ('producto', 'relacion_tipo_criticidad')  # Evita duplicados

    def __str__(self):
        relacion = self.relacion_tipo_criticidad
        return f"{self.producto.name} - {relacion.tipo_criticidad.name} ({relacion.criticidad.name})"
    
class TipoEquipo(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Tipo de Equipo"
        verbose_name_plural = "Tipos de Equipo"

    def __str__(self):
        return f"{self.name}"

class TipoEquipoProducto(BaseModel):
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE)
    relacion_producto = models.ForeignKey(ProductoTipoCritCrit, on_delete=models.CASCADE, related_name='tipos_equipo')

    class Meta:
        unique_together = ('tipo_equipo', 'relacion_producto')  # Evita duplicados

    def __str__(self):
        relacion = self.relacion_producto
        return f"{self.tipo_equipo.name} - {relacion.producto.name} ({relacion.relacion_tipo_criticidad.tipo_criticidad.name} - {relacion.relacion_tipo_criticidad.criticidad.name})"
    
class Tecnologia(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Tecnología"
        verbose_name_plural = "Tecnologías"

    def __str__(self):
        return f"{self.name}"

class TecnologiaTipoEquipo(BaseModel):
    tecnologia = models.ForeignKey(Tecnologia, on_delete=models.CASCADE)
    relacion_tipo_equipo = models.ForeignKey(TipoEquipoProducto, on_delete=models.CASCADE, related_name='tecnologias')

    class Meta:
        unique_together = ('tecnologia', 'relacion_tipo_equipo')  # Evita duplicados

    def __str__(self):
        relacion = self.relacion_tipo_equipo
        return f"{self.tecnologia.name} - {relacion.tipo_equipo.name} ({relacion.relacion_producto.producto.name} - {relacion.relacion_producto.relacion_tipo_criticidad.tipo_criticidad.name} - {relacion.relacion_producto.relacion_tipo_criticidad.criticidad.name})"
    
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