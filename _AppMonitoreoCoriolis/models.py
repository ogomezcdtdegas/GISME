from django.db import models
from _AppCommon.models import BaseModel

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

