from django.db import models
from _AppCommon.models import BaseModel

class NodeRedData(BaseModel):
    sensor = models.CharField(max_length=100)
    valor = models.FloatField()

    def __str__(self):
        return f"{self.sensor}: {self.valor}"

# Create your models here.
