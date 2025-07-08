#!/usr/bin/env python3
"""
Script para verificar los datos que devuelve el serializer de TipoCriticidad.
"""

import os
import sys
import django

# Configurar Django
sys.path.append('d:/EQ-456/Escritorio/GISME')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import TipoCriticidad, Criticidad, TipoCriticidadCriticidad
from _AppComplementos.serializers import TipoCriticidadCriticidadSerializer
from django.db.models import Count

def verificar_datos_tipo_criticidad():
    """Verificar qué datos están devolviendo las queries."""
    print("🔍 Verificando datos de Tipo de Criticidad...")
    
    # 1. Verificar qué tipos de criticidad existen
    tipos = TipoCriticidad.objects.all()
    print(f"\n📊 Tipos de Criticidad encontrados: {tipos.count()}")
    for tipo in tipos:
        print(f"   - {tipo.name} (ID: {tipo.id})")
    
    # 2. Verificar relaciones TipoCriticidadCriticidad
    relaciones = TipoCriticidadCriticidad.objects.all()
    print(f"\n🔗 Relaciones TipoCriticidadCriticidad encontradas: {relaciones.count()}")
    for rel in relaciones:
        print(f"   - {rel.tipo_criticidad.name} → {rel.criticidad.name}")
    
    # 3. Verificar query con anotaciones (como en el serializer)
    queryset = TipoCriticidadCriticidad.objects.select_related(
        'tipo_criticidad', 'criticidad'
    ).annotate(
        total_relations=Count('tipo_criticidad')
    ).order_by('tipo_criticidad__name')
    
    print(f"\n📈 Query con anotaciones: {queryset.count()}")
    for item in queryset:
        print(f"   - {item.tipo_criticidad.name} → {item.criticidad.name} (total_relations: {item.total_relations})")
    
    # 4. Simular serialización
    serializer = TipoCriticidadCriticidadSerializer(queryset, many=True)
    print(f"\n🔄 Datos serializados:")
    for item in serializer.data:
        print(f"   - tipo_criticidad_id: {item['tipo_criticidad_id']}")
        print(f"     tipo_criticidad_name: {item['tipo_criticidad_name']}")
        print(f"     criticidad_name: {item['criticidad_name']}")
        print(f"     total_relations: {item['total_relations']}")
        print(f"     ---")

def crear_datos_prueba_agrupacion():
    """Crear datos específicos para probar la agrupación."""
    print("\n🔄 Creando datos de prueba para agrupación...")
    
    try:
        # Crear criticidades
        crit1 = Criticidad.objects.get_or_create(name="Crit1")[0]
        crit2 = Criticidad.objects.get_or_create(name="Crit2")[0]
        
        # Crear tipo de criticidad
        tipo_crit1 = TipoCriticidad.objects.get_or_create(name="TipCrit1")[0]
        
        # Crear relaciones (múltiples para el mismo tipo)
        rel1 = TipoCriticidadCriticidad.objects.get_or_create(
            tipo_criticidad=tipo_crit1,
            criticidad=crit1
        )[0]
        
        rel2 = TipoCriticidadCriticidad.objects.get_or_create(
            tipo_criticidad=tipo_crit1,
            criticidad=crit2
        )[0]
        
        print(f"✅ Datos creados:")
        print(f"   - Tipo: {tipo_crit1.name}")
        print(f"   - Relación 1: {rel1.tipo_criticidad.name} → {rel1.criticidad.name}")
        print(f"   - Relación 2: {rel2.tipo_criticidad.name} → {rel2.criticidad.name}")
        
    except Exception as e:
        print(f"ℹ️  Error o datos ya existentes: {e}")

if __name__ == "__main__":
    crear_datos_prueba_agrupacion()
    verificar_datos_tipo_criticidad()
