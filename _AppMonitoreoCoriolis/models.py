from django.db import models
from _AppCommon.models import BaseModel
"""
class NodeRedData(BaseModel):
    tag_Sistema = models.CharField(max_length=100, null=True, blank=True)
    volumen_total = models.FloatField(null=True, blank=True)
    volumen_fwd = models.FloatField(null=True, blank=True)
    volumen_rev = models.FloatField(null=True, blank=True)
    masa_total = models.FloatField(null=True, blank=True)
    masa_fwd = models.FloatField(null=True, blank=True)
    masa_rev = models.FloatField(null=True, blank=True)
    densidad = models.FloatField(null=True, blank=True)
    volumen_60f = models.FloatField(null=True, blank=True)
    grav_spec_60f = models.FloatField(null=True, blank=True)
    caudal_rate = models.FloatField(null=True, blank=True)
    mass_rate = models.FloatField(null=True, blank=True)
    temperatura_coriolis = models.FloatField(null=True, blank=True)
    temperatura_diagnostico = models.FloatField(null=True, blank=True)
    temperatura_redundante = models.FloatField(null=True, blank=True)
    presion = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.tag_Sistema}"
"""

class NodeRedData(BaseModel):
    tag_Sistema = models.CharField(max_length=100, null=True, blank=True)
    volumen_total = models.FloatField(null=True, blank=True)
    volumen_fwd = models.FloatField(null=True, blank=True)
    volumen_rev = models.FloatField(null=True, blank=True)
    masa_total = models.FloatField(null=True, blank=True)
    masa_fwd = models.FloatField(null=True, blank=True)
    masa_rev = models.FloatField(null=True, blank=True)
    densidad = models.FloatField(null=True, blank=True)
    volumen_60f = models.FloatField(null=True, blank=True)
    grav_spec_60f = models.FloatField(null=True, blank=True)
    caudal_rate = models.FloatField(null=True, blank=True)
    mass_rate = models.FloatField(null=True, blank=True)
    temperatura_coriolis = models.FloatField(null=True, blank=True)
    temperatura_diagnostico = models.FloatField(null=True, blank=True)
    temperatura_redundante = models.FloatField(null=True, blank=True)
    presion = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.tag_Sistema}"
# Create your models here.

