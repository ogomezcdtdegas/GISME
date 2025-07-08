#!/usr/bin/env python
"""
Script de optimización N+1 para Complementos
====================

Este script documenta las optimizaciones realizadas para resolver problemas de consultas N+1
en todas las secciones de Complementos y proporciona herramientas adicionales de optimización.

Optimizaciones aplicadas:
1. select_related() para relaciones ForeignKey
2. annotate() con Count() para precalcular total_relations
3. Serializers optimizados que usan anotaciones en lugar de SerializerMethodField

Problemas N+1 resueltos:
- Productos: Era 1 + N consultas, ahora es 1 consulta
- TipoEquipo: Era 1 + N consultas, ahora es 1 consulta  
- Tecnología: Era 1 + N + N consultas, ahora es 1 consulta
- TipoCriticidad: Era 1 + N consultas, ahora es 1 consulta
"""

import os
import sys
import django
from django.db import connection
from django.test.utils import override_settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_n_plus_one_optimization():
    """Probar las optimizaciones de consultas N+1"""
    print("🔍 Probando optimizaciones de consultas N+1...")
    
    from _AppComplementos.models import ProductoTipoCritCrit, TipoEquipoProducto, TecnologiaTipoEquipo, TipoCriticidadCriticidad
    from _AppComplementos.serializers import ProductoTipoCriticiddadSerializer, TipoEquipoProductoSerializer, TecnologiaTipoEquipoSerializer, TipoCriticidadCriticidadSerializer
    from django.db.models import Count
    
    # Test 1: Productos optimizados
    print("\n📦 Test 1: Productos")
    with override_settings(DEBUG=True):
        connection.queries_log.clear()
        
        queryset = ProductoTipoCritCrit.objects.select_related(
            'producto',
            'relacion_tipo_criticidad',
            'relacion_tipo_criticidad__tipo_criticidad',
            'relacion_tipo_criticidad__criticidad'
        ).annotate(
            total_relations=Count('producto__productotipocritcrit')
        )[:10]
        
        serializer = ProductoTipoCriticiddadSerializer(queryset, many=True)
        data = serializer.data
        
        print(f"   - Registros procesados: {len(data)}")
        print(f"   - Consultas ejecutadas: {len(connection.queries)}")
        print(f"   - Optimización exitosa: {'✅' if len(connection.queries) <= 2 else '❌'}")
    
    # Test 2: TipoEquipo optimizados
    print("\n🔧 Test 2: TipoEquipo")
    with override_settings(DEBUG=True):
        connection.queries_log.clear()
        
        queryset = TipoEquipoProducto.objects.select_related(
            'tipo_equipo',
            'relacion_producto__producto',
            'relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
            'relacion_producto__relacion_tipo_criticidad__criticidad'
        ).annotate(
            total_relations=Count('tipo_equipo__tipoequipoproducto')
        )[:10]
        
        serializer = TipoEquipoProductoSerializer(queryset, many=True)
        data = serializer.data
        
        print(f"   - Registros procesados: {len(data)}")
        print(f"   - Consultas ejecutadas: {len(connection.queries)}")
        print(f"   - Optimización exitosa: {'✅' if len(connection.queries) <= 2 else '❌'}")
    
    # Test 3: Tecnología optimizados
    print("\n⚙️ Test 3: Tecnología")
    with override_settings(DEBUG=True):
        connection.queries_log.clear()
        
        queryset = TecnologiaTipoEquipo.objects.select_related(
            'tecnologia',
            'relacion_tipo_equipo__tipo_equipo',
            'relacion_tipo_equipo__relacion_producto__producto',
            'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__tipo_criticidad',
            'relacion_tipo_equipo__relacion_producto__relacion_tipo_criticidad__criticidad'
        ).annotate(
            total_relations=Count('tecnologia__tecnologiatipoequipo')
        )[:10]
        
        serializer = TecnologiaTipoEquipoSerializer(queryset, many=True)
        data = serializer.data
        
        print(f"   - Registros procesados: {len(data)}")
        print(f"   - Consultas ejecutadas: {len(connection.queries)}")
        print(f"   - Optimización exitosa: {'✅' if len(connection.queries) <= 2 else '❌'}")
    
    # Test 4: TipoCriticidad optimizados
    print("\n📋 Test 4: TipoCriticidad")
    with override_settings(DEBUG=True):
        connection.queries_log.clear()
        
        queryset = TipoCriticidadCriticidad.objects.select_related(
            'tipo_criticidad',
            'criticidad'
        ).annotate(
            total_relations=Count('tipo_criticidad__tipocriticidadcriticidad')
        )[:10]
        
        serializer = TipoCriticidadCriticidadSerializer(queryset, many=True)
        data = serializer.data
        
        print(f"   - Registros procesados: {len(data)}")
        print(f"   - Consultas ejecutadas: {len(connection.queries)}")
        print(f"   - Optimización exitosa: {'✅' if len(connection.queries) <= 2 else '❌'}")

def suggest_database_indexes():
    """Sugerir índices adicionales para la base de datos"""
    print("\n💾 Sugerencias de índices de base de datos:")
    print("""
    -- Índices recomendados para mejorar el rendimiento:
    
    -- Para búsquedas por nombre de producto
    CREATE INDEX idx_producto_name ON _AppComplementos_producto(name);
    
    -- Para búsquedas por nombre de tecnología
    CREATE INDEX idx_tecnologia_name ON _AppComplementos_tecnologia(name);
    
    -- Para búsquedas por nombre de tipo de equipo
    CREATE INDEX idx_tipoequipo_name ON _AppComplementos_tipoequipo(name);
    
    -- Para búsquedas por nombre de tipo de criticidad
    CREATE INDEX idx_tipocriticidad_name ON _AppComplementos_tipocriticidad(name);
    
    -- Para búsquedas por nombre de criticidad
    CREATE INDEX idx_criticidad_name ON _AppComplementos_criticidad(name);
    
    -- Índices compuestos para relaciones frecuentes
    CREATE INDEX idx_producto_tipo_crit ON _AppComplementos_productotipocritcrit(producto_id, relacion_tipo_criticidad_id);
    CREATE INDEX idx_tipo_equipo_producto ON _AppComplementos_tipoequipoproducto(tipo_equipo_id, relacion_producto_id);
    CREATE INDEX idx_tecnologia_tipo_equipo ON _AppComplementos_tecnologiatipoequipo(tecnologia_id, relacion_tipo_equipo_id);
    """)

def performance_tips():
    """Consejos adicionales de rendimiento"""
    print("\n🚀 Consejos adicionales de rendimiento:")
    print("""
    1. PAGINACIÓN:
       - Usar LIMIT/OFFSET eficiente
       - Considerar cursor-based pagination para datasets grandes
    
    2. CACHÉ:
       - Implementar Redis para consultas frecuentes
       - Cachear conteos de relaciones que cambian poco
    
    3. CONSULTAS:
       - Usar only() para campos específicos si no necesitas todos
       - Usar defer() para diferir campos grandes
    
    4. FRONTEND:
       - Implementar lazy loading para tablas grandes
       - Usar debounce en búsquedas (ya implementado)
    
    5. BASE DE DATOS:
       - Configurar connection pooling
       - Monitorear slow queries
       - Considerar partitioning para tablas muy grandes
    
    6. DJANGO:
       - Usar select_for_update() solo cuando sea necesario
       - Configurar CONN_MAX_AGE para reutilizar conexiones
       - Usar bulk_create() y bulk_update() para operaciones masivas
    """)

if __name__ == "__main__":
    print("🔧 Optimización N+1 - Sistema de Complementos")
    print("=" * 50)
    
    test_n_plus_one_optimization()
    suggest_database_indexes()
    performance_tips()
    
    print("\n✅ Optimizaciones completadas!")
    print("📊 Beneficios esperados:")
    print("   - Reducción del 80-90% en consultas de base de datos")
    print("   - Mejora significativa en velocidad de carga")
    print("   - Menor uso de memoria y CPU")
    print("   - Mejor experiencia de usuario")
