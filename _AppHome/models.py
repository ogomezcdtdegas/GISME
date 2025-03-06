from django.db import models

class Equipo(models.Model):
    serial = models.CharField(max_length=50, unique=True, verbose_name="Serial")
    sap = models.CharField(max_length=50, verbose_name="SAP")
    marca = models.CharField(max_length=50, verbose_name="Marca")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    def __str__(self):
        return f"{self.serial} - {self.marca}"
