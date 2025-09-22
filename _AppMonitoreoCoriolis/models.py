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
    tag_system = models.CharField(max_length=100, null=True, blank=True)
    total_volume = models.FloatField(null=True, blank=True)
    forward_volume = models.FloatField(null=True, blank=True)
    reverse_volume = models.FloatField(null=True, blank=True)
    total_mass = models.FloatField(null=True, blank=True)
    forward_mass = models.FloatField(null=True, blank=True)
    reverse_mass = models.FloatField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    volume_60f = models.FloatField(null=True, blank=True)
    specific_gravity_60f = models.FloatField(null=True, blank=True)
    flow_rate = models.FloatField(null=True, blank=True)
    mass_rate = models.FloatField(null=True, blank=True)
    coriolis_temperature = models.FloatField(null=True, blank=True)
    diagnostic_temperature = models.FloatField(null=True, blank=True)
    redundant_temperature = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.tag_system}"
# Create your models here.

