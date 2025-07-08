"""
Script para crear datos de prueba específicos para verificar la agrupación por tipo_criticidad
"""

import os
import sys
import django

# Configurar Django
sys.path.append(r'd:\EQ-456\Escritorio\GISME')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import Criticidad, TipoCriticidad, TipoCriticidadCriticidad

def create_test_data():
    """Crear datos de prueba para verificar agrupación por tipo_criticidad"""
    print("🔹 Creando datos de prueba para agrupación por tipo_criticidad...")
    
    # Limpiar datos de prueba previos
    TipoCriticidadCriticidad.objects.filter(tipo_criticidad__name__startswith="TipoTest").delete()
    TipoCriticidadCriticidad.objects.filter(criticidad__name__startswith="CritTest").delete()
    TipoCriticidad.objects.filter(name__startswith="TipoTest").delete()
    Criticidad.objects.filter(name__startswith="CritTest").delete()
    
    # Crear criticidades
    crit1 = Criticidad.objects.create(name="CritTest Alpha")
    crit2 = Criticidad.objects.create(name="CritTest Beta")
    crit3 = Criticidad.objects.create(name="CritTest Gamma")
    
    # Crear tipos de criticidad
    tipo1 = TipoCriticidad.objects.create(name="TipoTest Uno")
    tipo2 = TipoCriticidad.objects.create(name="TipoTest Dos")
    tipo3 = TipoCriticidad.objects.create(name="TipoTest Tres")
    
    # Crear relaciones - para probar agrupación por tipo_criticidad
    # TipoTest Uno tendrá 3 criticidades (debe aparecer con rowspan=3)
    TipoCriticidadCriticidad.objects.create(tipo_criticidad=tipo1, criticidad=crit1)
    TipoCriticidadCriticidad.objects.create(tipo_criticidad=tipo1, criticidad=crit2)
    TipoCriticidadCriticidad.objects.create(tipo_criticidad=tipo1, criticidad=crit3)
    
    # TipoTest Dos tendrá 2 criticidades (debe aparecer con rowspan=2)
    TipoCriticidadCriticidad.objects.create(tipo_criticidad=tipo2, criticidad=crit1)
    TipoCriticidadCriticidad.objects.create(tipo_criticidad=tipo2, criticidad=crit2)
    
    # TipoTest Tres tendrá 1 criticidad (sin rowspan)
    TipoCriticidadCriticidad.objects.create(tipo_criticidad=tipo3, criticidad=crit1)
    
    print("✅ Datos de prueba creados:")
    print(f"   - {tipo1.name}: {TipoCriticidadCriticidad.objects.filter(tipo_criticidad=tipo1).count()} criticidades")
    print(f"   - {tipo2.name}: {TipoCriticidadCriticidad.objects.filter(tipo_criticidad=tipo2).count()} criticidades")
    print(f"   - {tipo3.name}: {TipoCriticidadCriticidad.objects.filter(tipo_criticidad=tipo3).count()} criticidades")
    
    print("\n🌐 Servidor corriendo en: http://127.0.0.1:8000/")
    print("📱 Navega a: http://127.0.0.1:8000/complementos/tipo_criticidad/")
    print("\n👁️ Verifica que:")
    print("   - TipoTest Uno aparece con rowspan=3 (3 criticidades)")
    print("   - TipoTest Dos aparece con rowspan=2 (2 criticidades)")
    print("   - TipoTest Tres aparece sin rowspan (1 criticidad)")
    print("   - Los badges muestran el número correcto de relaciones")
    print("   - La primera columna muestra el Tipo de Criticidad")
    print("   - La segunda columna muestra las Criticidades")

if __name__ == "__main__":
    create_test_data()
