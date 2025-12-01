from django.db import models
from _AppCommon.models import BaseModel  # Importamos el modelo base


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
    tag = models.CharField(max_length=50, unique=True, verbose_name="Tag")
    sistema_id = models.CharField(max_length=50, unique=True, verbose_name="ID Sistema")
    identificacion_medidor = models.CharField(max_length=100, verbose_name="Identificación del Medidor", blank=True, null=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='sistemas', verbose_name="Ubicación")

    class Meta:
        verbose_name = "Sistema"
        verbose_name_plural = "Sistemas"

    def __str__(self):
        return f"{self.tag} - {self.sistema_id} ({self.ubicacion.nombre})"


class ConfiguracionCoeficientes(BaseModel):
    systemId = models.ForeignKey(
        Sistema,
        on_delete=models.CASCADE,
        related_name='coeficientes',
        verbose_name="Sistema"
    )
    mt = models.FloatField(verbose_name="M Temperatura")
    bt = models.FloatField(verbose_name="B Temperatura")
    mp = models.FloatField(verbose_name="M Presión")
    bp = models.FloatField(verbose_name="B Presión")
    zero_presion = models.FloatField(verbose_name="Zero Presión", default=0.0)
    span_presion = models.FloatField(verbose_name="Span Presión", default=1.0)
    lim_inf_caudal_masico = models.FloatField(verbose_name="Límite Inferior Caudal Másico", default=0.0)
    lim_sup_caudal_masico = models.FloatField(verbose_name="Límite Superior Caudal Másico", default=1000000.0)
    vol_masico_ini_batch = models.FloatField(verbose_name="Volumen Másico Total para confirmación de bath", default=0.0)
    # num_ticket se mantiene en el modelo por compatibilidad con la BD, pero ya no se usa en la interfaz
    # Los tickets ahora se generan automáticamente con formato Sistema-FechaHora en BatchDetectado
    num_ticket = models.IntegerField(verbose_name="Número de Ticket", default=1)
    time_finished_batch = models.FloatField(
        verbose_name="Tiempo de espera para cierre de batch (minutos)",
        default=2.0,
        help_text="Minutos que deben pasar en cero para confirmar cierre de batch"
    )

    # ===============================
    # Incertidumbre - Variables Medición
    # ===============================
    tipo_met = models.CharField(max_length=50, default="Coriolis", verbose_name="Tipo de medidor")  # id: tipoMet
    dl = models.FloatField(null=True, blank=True, verbose_name="Densidad (kg/m³)")  # id: dl
    product = models.CharField(max_length=50, default="GLP", verbose_name="Tipo de fluido")  # id: product
    tl = models.FloatField(null=True, blank=True, verbose_name="Temperatura de líquido promedio (°F)")  # id: Tl
    pl = models.FloatField(null=True, blank=True, verbose_name="Presión de líquido promedio (psi)")  # id: Pl
    masa = models.FloatField(null=True, blank=True, verbose_name="Masa indicada por el medidor (kg)")  # id: Masa
    mf = models.FloatField(null=True, blank=True, verbose_name="Factor de corrección del medidor (-)")  # id: MF
    qm = models.FloatField(null=True, blank=True, verbose_name="Caudal másico promedio (kg/h)")  # id: Qm
    vis = models.FloatField(null=True, blank=True, verbose_name="Viscosidad dinámica (cP)")  # id: vis
    deltavis = models.FloatField(null=True, blank=True, verbose_name="Rango viscosidad (cP)")  # id: deltavis
    dn = models.FloatField(null=True, blank=True, verbose_name="Diámetro nominal (in)")  # id: DN

    # ===============================
    # Incertidumbre - Medición de Densidad
    # ===============================
    metdl = models.CharField(max_length=100, null=True, blank=True, verbose_name="Método de análisis densidad")  # id: metdl
    ucal_dens = models.FloatField(null=True, blank=True, verbose_name="Incertidumbre calibración densitómetro (kg/m³)")  # id: ucalDens
    kcal_dens = models.FloatField(null=True, blank=True, verbose_name="Factor de cobertura densitómetro (-)")  # id: kcalDens
    tipdens = models.CharField(max_length=100, null=True, blank=True, verbose_name="Tipo de densitómetro")  # id: tipdens
    desv_dens = models.FloatField(null=True, blank=True, verbose_name="Desviación viscosidad (kg/m³)")  # id: desvdens

    # ===============================
    # Incertidumbre - Características del Medidor
    # ===============================
    ucal_met = models.FloatField(null=True, blank=True, verbose_name="Incertidumbre calibración medidor (%)")  # id: ucalMet
    kcal_met = models.FloatField(null=True, blank=True, verbose_name="Factor de cobertura medidor")  # id: kcalMet
    esis_met = models.FloatField(null=True, blank=True, verbose_name="Error máximo medidor (%)")  # id: esisMet
    ucarta_met = models.FloatField(null=True, blank=True, verbose_name="Incertidumbre carta medidor (%)")  # id: ucartaMet
    zero_stab = models.FloatField(null=True, blank=True, verbose_name="Estabilidad en cero medidor (Kg/m³)")  # id: zeroStab

    # ===============================
    # Diagnóstico del Coriolis
    # ===============================
    diagnostic_glp_density_ref = models.FloatField(
        null=True,
        blank=True,
        default=0.55,
        verbose_name="Densidad GLP de referencia (g/cc)",
        help_text="Valor nominal de la densidad del GLP usado para estimar porcentaje de agua"
    )
    diagnostic_glp_density_tolerance_pct = models.FloatField(
        null=True,
        blank=True,
        default=5.0,
        verbose_name="Variación permitida densidad GLP (%)",
        help_text="Margen porcentual para considerar variaciones naturales del GLP"
    )
    diagnostic_driver_amp_base = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Driver Amp base (mA)",
        help_text="Corriente de referencia del driver para detectar incrementos anómalos"
    )
    diagnostic_driver_amp_multiplier = models.FloatField(
        null=True,
        blank=True,
        default=1.3,
        verbose_name="Multiplicador alerta Driver Amp",
        help_text="Factor multiplicador aplicado al valor base para marcar alerta"
    )
    diagnostic_n1_threshold = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Umbral N1",
        help_text="Valor máximo esperado para el ruido estimado N1"
    )
    diagnostic_n2_threshold = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Umbral N2",
        help_text="Valor máximo esperado para el ruido estimado N2"
    )
    diagnostic_amp_imbalance_threshold_pct = models.FloatField(
        null=True,
        blank=True,
        default=5.0,
        verbose_name="Umbral desbalance A1/A2 (%)",
        help_text="Porcentaje de desbalance entre A1 y A2 a partir del cual se reporta alerta"
    )

    class Meta:
        verbose_name = "Configuración de Coeficientes"
        verbose_name_plural = "Configuraciones de Coeficientes"
        unique_together = ['systemId']  # Un sistema solo puede tener una configuración de coeficientes

    def __str__(self):
        return f"Coeficientes de {self.systemId.tag} (T: y={self.mt}x+{self.bt}, P: y={self.mp}x+{self.bp})"
