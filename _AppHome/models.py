from django.db import models
from _AppCommon.models import BaseModel  # Importamos el modelo base


class Equipo(BaseModel):
    serial = models.CharField(max_length=100, unique=True)
    sap = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"

    def __str__(self):
        return f"{self.serial} - {self.sap} - {self.marca}"
