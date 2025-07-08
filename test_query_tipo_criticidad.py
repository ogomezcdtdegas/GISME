"""
Script para probar la query correcta para agrupar por tipo_criticidad
"""

import os
import sys
import django

# Configurar Django
sys.path.append(r'd:\EQ-456\Escritorio\GISME')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import TipoCriticidadCriticidad
from django.db.models import Count

def test_query_tipo_criticidad():
    """Probar la query correcta para agrupar por tipo_criticidad"""
    print("🔹 Probando query para agrupar por tipo_criticidad...")
    
    # Probar diferentes formas de hacer la query
    try:
        # Forma 1: Usando el nombre por defecto
        print("Probando: Count('tipo_criticidad__tipocriticidadcriticidad')")
        queryset1 = TipoCriticidadCriticidad.objects.annotate(
            total_relations=Count('tipo_criticidad__tipocriticidadcriticidad')
        )
        print("✅ Funciona")
        for obj in queryset1[:3]:
            print(f"  - {obj.tipo_criticidad.name}: {obj.total_relations}")
    except Exception as e:
        print(f"❌ Error: {e}")
        
    try:
        # Forma 2: Usando el related_name por defecto al revés
        print("\nProbando: Count('tipo_criticidad__tipocriticidadcriticidad_set')")
        queryset2 = TipoCriticidadCriticidad.objects.annotate(
            total_relations=Count('tipo_criticidad__tipocriticidadcriticidad_set')
        )
        print("✅ Funciona")
        for obj in queryset2[:3]:
            print(f"  - {obj.tipo_criticidad.name}: {obj.total_relations}")
    except Exception as e:
        print(f"❌ Error: {e}")
        
    # Forma 3: Manera más directa
    try:
        print("\nProbando query directa por tipo_criticidad...")
        from django.db.models import Q
        
        # Obtener todos los TipoCriticidad y contar manualmente
        tipo_criticidades = {}
        for obj in TipoCriticidadCriticidad.objects.select_related('tipo_criticidad', 'criticidad'):
            tipo_id = obj.tipo_criticidad.id
            if tipo_id not in tipo_criticidades:
                tipo_criticidades[tipo_id] = {
                    'name': obj.tipo_criticidad.name,
                    'count': 0
                }
            tipo_criticidades[tipo_id]['count'] += 1
            
        print("✅ Conteo manual:")
        for tipo_id, data in list(tipo_criticidades.items())[:5]:
            print(f"  - {data['name']}: {data['count']} relaciones")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_query_tipo_criticidad()
