"""
Script para probar visualmente que la agrupación funciona correctamente
después de las correcciones realizadas.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(r'd:\EQ-456\Escritorio\GISME')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import Criticidad, TipoCriticidad, TipoCriticidadCriticidad

def test_visual_grouping():
    """Crear datos de prueba para verificar visualmente que la agrupación funciona"""
    print("🔹 Creando datos de prueba para verificación visual...")
    
    # Limpiar datos de prueba previos
    TipoCriticidadCriticidad.objects.filter(criticidad__name__startswith="Test Visual").delete()
    TipoCriticidad.objects.filter(name__startswith="TipoTest").delete()
    Criticidad.objects.filter(name__startswith="Test Visual").delete()
    
    # Crear criticidades
    criticidad1 = Criticidad.objects.create(name="Test Visual Criticidad 1")
    criticidad2 = Criticidad.objects.create(name="Test Visual Criticidad 2")
    criticidad3 = Criticidad.objects.create(name="Test Visual Criticidad 3")
    
    # Crear tipos de criticidad
    tipo1 = TipoCriticidad.objects.create(name="TipoTest A")
    tipo2 = TipoCriticidad.objects.create(name="TipoTest B")
    tipo3 = TipoCriticidad.objects.create(name="TipoTest C")
    tipo4 = TipoCriticidad.objects.create(name="TipoTest D")
    
    # Crear relaciones - para probar agrupación
    # Criticidad1 tendrá 3 tipos (se debe agrupar con rowspan=3)
    TipoCriticidadCriticidad.objects.create(criticidad=criticidad1, tipo_criticidad=tipo1)
    TipoCriticidadCriticidad.objects.create(criticidad=criticidad1, tipo_criticidad=tipo2)
    TipoCriticidadCriticidad.objects.create(criticidad=criticidad1, tipo_criticidad=tipo3)
    
    # Criticidad2 tendrá 2 tipos (se debe agrupar con rowspan=2)
    TipoCriticidadCriticidad.objects.create(criticidad=criticidad2, tipo_criticidad=tipo1)
    TipoCriticidadCriticidad.objects.create(criticidad=criticidad2, tipo_criticidad=tipo4)
    
    # Criticidad3 tendrá 1 tipo (sin agrupación)
    TipoCriticidadCriticidad.objects.create(criticidad=criticidad3, tipo_criticidad=tipo2)
    
    print("✅ Datos de prueba creados:")
    print(f"   - {criticidad1.name}: {TipoCriticidadCriticidad.objects.filter(criticidad=criticidad1).count()} tipos")
    print(f"   - {criticidad2.name}: {TipoCriticidadCriticidad.objects.filter(criticidad=criticidad2).count()} tipos")
    print(f"   - {criticidad3.name}: {TipoCriticidadCriticidad.objects.filter(criticidad=criticidad3).count()} tipos")
    
    print("\n🌐 Servidor corriendo en: http://127.0.0.1:8000/")
    print("📱 Navega a: http://127.0.0.1:8000/complementos/tipo_criticidad/")
    print("\n👁️ Verifica que:")
    print("   - Test Visual Criticidad 1 aparece con rowspan=3")
    print("   - Test Visual Criticidad 2 aparece con rowspan=2")
    print("   - Test Visual Criticidad 3 aparece sin rowspan")
    print("   - Los badges muestran el número correcto de relaciones")
    
    print("\n🔧 Para limpiar los datos de prueba, ejecuta:")
    print("   python test_visual_cleanup.py")

if __name__ == "__main__":
    test_visual_grouping()
