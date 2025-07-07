#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import TipoCriticidadCriticidad
from _AppComplementos.serializers import TipoCriticidadCriticidadSerializer

print("Probando serializer TipoCriticidadCriticidad...")

try:
    # Obtener algunos registros
    queryset = TipoCriticidadCriticidad.objects.select_related('tipo_criticidad', 'criticidad').all()[:5]
    print(f"Registros encontrados: {queryset.count()}")
    
    # Serializar los datos
    serializer = TipoCriticidadCriticidadSerializer(queryset, many=True)
    data = serializer.data
    print(f"Serialización exitosa. Datos: {len(data)} registros")
    
    # Imprimir el primer registro si existe
    if data:
        print(f"Primer registro: {data[0]}")
        
    print("✅ Serializer funciona correctamente")
    
except Exception as e:
    print(f"❌ Error en serializer: {e}")
    import traceback
    traceback.print_exc()
