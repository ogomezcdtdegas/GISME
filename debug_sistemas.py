#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from _AppComplementos.models import Sistema, Ubicacion
from _AppComplementos.serializers import SistemaSerializer

def debug_sistemas():
    print("🔍 Debugging Sistemas en la base de datos...")
    
    # Verificar sistemas
    sistemas = Sistema.objects.all()
    print(f"📊 Total de sistemas: {sistemas.count()}")
    
    for sistema in sistemas:
        print(f"\n🔸 Sistema ID: {sistema.id}")
        print(f"   Tag: {sistema.tag}")
        print(f"   Sistema ID: {sistema.sistema_id}")
        print(f"   Ubicacion: {sistema.ubicacion}")
        
        if sistema.ubicacion:
            print(f"   Ubicacion nombre: {sistema.ubicacion.nombre}")
            print(f"   Latitud: {sistema.ubicacion.latitud} (tipo: {type(sistema.ubicacion.latitud)})")
            print(f"   Longitud: {sistema.ubicacion.longitud} (tipo: {type(sistema.ubicacion.longitud)})")
            
            # Probar el serializer
            try:
                serializer = SistemaSerializer(sistema)
                data = serializer.data
                print(f"   ✅ Serializer OK: {data.get('ubicacion_coordenadas', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Error en serializer: {str(e)}")
        else:
            print(f"   ❌ Sin ubicacion")

if __name__ == "__main__":
    debug_sistemas()
