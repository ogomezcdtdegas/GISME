from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_AppComplementos', '0014_configuracioncoeficientes_deltavis_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracioncoeficientes',
            name='diagnostic_amp_imbalance_threshold_pct',
            field=models.FloatField(blank=True, default=5.0, help_text='Porcentaje de desbalance entre A1 y A2 a partir del cual se reporta alerta', null=True, verbose_name='Umbral desbalance A1/A2 (%)'),
        ),
        migrations.AddField(
            model_name='configuracioncoeficientes',
            name='diagnostic_driver_amp_base',
            field=models.FloatField(blank=True, help_text='Corriente de referencia del driver para detectar incrementos anómalos', null=True, verbose_name='Driver Amp base (mA)'),
        ),
        migrations.AddField(
            model_name='configuracioncoeficientes',
            name='diagnostic_driver_amp_multiplier',
            field=models.FloatField(blank=True, default=1.3, help_text='Factor multiplicador aplicado al valor base para marcar alerta', null=True, verbose_name='Multiplicador alerta Driver Amp'),
        ),
        migrations.AddField(
            model_name='configuracioncoeficientes',
            name='diagnostic_glp_density_ref',
            field=models.FloatField(blank=True, default=0.55, help_text='Valor nominal de la densidad del GLP usado para estimar porcentaje de agua', null=True, verbose_name='Densidad GLP de referencia (g/cc)'),
        ),
        migrations.AddField(
            model_name='configuracioncoeficientes',
            name='diagnostic_glp_density_tolerance_pct',
            field=models.FloatField(blank=True, default=5.0, help_text='Margen porcentual para considerar variaciones naturales del GLP', null=True, verbose_name='Variación permitida densidad GLP (%)'),
        ),
        migrations.AddField(
            model_name='configuracioncoeficientes',
            name='diagnostic_n1_threshold',
            field=models.FloatField(blank=True, help_text='Valor máximo esperado para el ruido estimado N1', null=True, verbose_name='Umbral N1'),
        ),
        migrations.AddField(
            model_name='configuracioncoeficientes',
            name='diagnostic_n2_threshold',
            field=models.FloatField(blank=True, help_text='Valor máximo esperado para el ruido estimado N2', null=True, verbose_name='Umbral N2'),
        ),
    ]
