from django.db import models
from _AppCommon.models import BaseModel
from _AppComplementos.models import Sistema

class NodeRedData(BaseModel):
    systemId = models.ForeignKey(Sistema, on_delete=models.CASCADE, related_name='nodered_data')

    mac_gateway = models.CharField(max_length=100, null=True, blank=True)

    created_at_iot = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora del IoT")

    total_volume = models.FloatField(null=True, blank=True)
    forward_volume = models.FloatField(null=True, blank=True)
    reverse_volume = models.FloatField(null=True, blank=True)
    vol_rate_alm = models.FloatField(null=True, blank=True)
    flow_rate = models.FloatField(null=True, blank=True)

    total_mass = models.FloatField(null=True, blank=True)
    forward_mass = models.FloatField(null=True, blank=True)
    reverse_mass = models.FloatField(null=True, blank=True)
    mass_rate_alm = models.FloatField(null=True, blank=True)
    mass_rate = models.FloatField(null=True, blank=True)

    density = models.FloatField(null=True, blank=True)
    density_alm = models.FloatField(null=True, blank=True)

    volume_60f = models.FloatField(null=True, blank=True)
    specific_gravity_60f = models.FloatField(null=True, blank=True)

    coriolis_temperature = models.FloatField(null=True, blank=True)
    coriolis_temperature_alm = models.FloatField(null=True, blank=True)

    diagnostic_temperature = models.FloatField(null=True, blank=True)
    diagnostic_temperature_alm = models.FloatField(null=True, blank=True)

    redundant_temperature = models.FloatField(null=True, blank=True)

    pressure_in = models.FloatField(null=True, blank=True)
    pressure_out = models.FloatField(null=True, blank=True)

    coriolis_frecuency = models.FloatField(null=True, blank=True)
    coriolis_frecuency_alm = models.FloatField(null=True, blank=True)

    total_conc = models.FloatField(null=True, blank=True)
    forward_conc = models.FloatField(null=True, blank=True)
    reverse_conc = models.FloatField(null=True, blank=True)
    conc_rate = models.FloatField(null=True, blank=True)
    conc_rate_alm = models.FloatField(null=True, blank=True)
    pconc = models.FloatField(null=True, blank=True)
    pconc_alm = models.FloatField(null=True, blank=True)

    total_productionWater = models.FloatField(null=True, blank=True)
    forward_productionWater = models.FloatField(null=True, blank=True)
    reverse_productionWater = models.FloatField(null=True, blank=True)
    productionWater_rate = models.FloatField(null=True, blank=True)
    productionWater_rate_alm = models.FloatField(null=True, blank=True)

    percent_cutWater16b = models.FloatField(null=True, blank=True)
    percent_cutWater64b = models.FloatField(null=True, blank=True)
    percent_cutWater_alm = models.FloatField(null=True, blank=True)

    driver_curr = models.FloatField(null=True, blank=True)
    driver_curr_alm = models.FloatField(null=True, blank=True)

    dsp_rxmsg_amplitudeEstimateA1 = models.FloatField(null=True, blank=True)
    dsp_rxmsg_amplitudeEstimateA2 = models.FloatField(null=True, blank=True)

    dsp_rxmsg_driverAmplitude=models.FloatField(null=True, blank=True)
    dsp_rxmsg_noiseEstimatedN1=models.FloatField(null=True, blank=True)
    dsp_rxmsg_noiseEstimatedN2=models.FloatField(null=True, blank=True)

    signal_strength_rxCoriolis = models.FloatField(null=True, blank=True)
    temperature_gateway = models.FloatField(null=True, blank=True)

    # Coeficientes de corrección vigentes al momento del registro
    mt = models.FloatField(null=True, blank=True, verbose_name="M Temperatura", help_text="Coeficiente M para temperatura de salida vigente al momento del registro")
    bt = models.FloatField(null=True, blank=True, verbose_name="B Temperatura", help_text="Coeficiente B para temperatura de salida vigente al momento del registro")
    mp = models.FloatField(null=True, blank=True, verbose_name="M Presión", help_text="Coeficiente M para presión vigente al momento del registro")
    bp = models.FloatField(null=True, blank=True, verbose_name="B Presión", help_text="Coeficiente B para presión vigente al momento del registro")

    def __str__(self):
        return f"{self.systemId}"


class BatchDetectado(BaseModel):
    """
    Modelo para almacenar los batches detectados automáticamente
    """
    systemId = models.ForeignKey(Sistema, on_delete=models.CASCADE, related_name='batches_detectados')
    
    fecha_inicio = models.DateTimeField(verbose_name="Fecha de Inicio del Batch")
    fecha_fin = models.DateTimeField(verbose_name="Fecha de Fin del Batch")
    vol_total = models.FloatField(verbose_name="Volumen Total Acumulado (gal)")
    mass_total = models.FloatField(verbose_name="Masa Total Acumulada (kg)", default=0.0)
    temperatura_coriolis_prom = models.FloatField(verbose_name="Temperatura Coriolis Promedio (°C)")
    densidad_prom = models.FloatField(verbose_name="Densidad Promedio (g/cc)")
    pressure_out_prom = models.FloatField(verbose_name="Presión de Salida Promedio (PSI)", null=True, blank=True)
    
    # Hash para identificación única basado en fechas, sistema y configuración
    hash_identificacion = models.CharField(max_length=64, unique=True, default='', verbose_name="Hash de Identificación")
    
    # Perfil de configuración usado para detectar este batch
    perfil_lim_inf_caudal = models.FloatField(verbose_name="Límite Inferior Caudal del Perfil (kg/h)", null=True, blank=True)
    perfil_lim_sup_caudal = models.FloatField(verbose_name="Límite Superior Caudal del Perfil (kg/h)", null=True, blank=True)
    perfil_vol_minimo = models.FloatField(verbose_name="Volumen Mínimo del Perfil (kg)", null=True, blank=True)
    
    # Información adicional del batch
    duracion_minutos = models.FloatField(verbose_name="Duración del Batch (minutos)", null=True, blank=True)
    total_registros = models.IntegerField(verbose_name="Total de Registros en el Batch", default=0)
    num_ticket = models.IntegerField(verbose_name="Número de Ticket asignado", null=True, blank=True)
    
    class Meta:
        verbose_name = "Batch Detectado"
        verbose_name_plural = "Batches Detectados"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        presion_str = f" - {self.pressure_out_prom:.1f} PSI" if self.pressure_out_prom else ""
        return f"Batch {self.systemId.tag} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')} ({self.vol_total:.2f} gal - {self.mass_total:.2f} kg{presion_str})"

# Create your models here.

