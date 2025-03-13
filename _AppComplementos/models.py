from django.db import models
from _AppCommon.models import BaseModel  # Importamos el modelo base


class Criticidad(BaseModel):
    name = models.CharField(max_length=100, unique=True)


    class Meta:
        verbose_name = "Criticidad"
        verbose_name_plural = "Criticidades"

    def __str__(self):
        return f"{self.name}"