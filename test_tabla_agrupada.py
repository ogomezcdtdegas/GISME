#!/usr/bin/env python
"""
Script para verificar la visualización de la tabla agrupada de productos
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import Producto, TipoCriticidad, Criticidad, TipoCriticidadCriticidad, ProductoTipoCritCrit

def verificar_datos_productos():
    """Verificar que hay datos suficientes para probar la agrupación"""
    
    print("🔍 Verificando datos de productos para agrupación...")
    
    # Contar productos y sus relaciones
    productos = Producto.objects.all()
    relaciones = ProductoTipoCritCrit.objects.all()
    
    print(f"📊 Total de productos: {productos.count()}")
    print(f"📊 Total de relaciones: {relaciones.count()}")
    
    # Mostrar productos con múltiples relaciones
    productos_con_multiples_relaciones = []
    for producto in productos:
        count = ProductoTipoCritCrit.objects.filter(producto=producto).count()
        if count > 1:
            productos_con_multiples_relaciones.append((producto.name, count))
    
    print(f"\n📋 Productos con múltiples combinaciones:")
    if productos_con_multiples_relaciones:
        for nombre, count in productos_con_multiples_relaciones:
            print(f"   • {nombre}: {count} combinaciones")
    else:
        print("   ❌ No hay productos con múltiples combinaciones")
    
    # Verificar la consulta optimizada
    print(f"\n🔧 Probando consulta optimizada...")
    
    from django.db import connection, reset_queries
    from django.db.models import Count
    
    # Resetear queries
    reset_queries()
    
    # Ejecutar la consulta optimizada
    queryset = ProductoTipoCritCrit.objects.select_related(
        'producto',
        'relacion_tipo_criticidad',
        'relacion_tipo_criticidad__tipo_criticidad',
        'relacion_tipo_criticidad__criticidad'
    ).annotate(
        total_relations=Count('producto__productotipocritcrit')
    ).order_by('producto__name', 'relacion_tipo_criticidad__tipo_criticidad__name')
    
    # Iterar para ejecutar la consulta
    result_list = list(queryset)
    
    query_count = len(connection.queries)
    print(f"✅ Consultas ejecutadas: {query_count}")
    print(f"📊 Registros obtenidos: {len(result_list)}")
    
    if query_count <= 2:  # Permitir 1-2 consultas máximo
        print("🚀 ¡Optimización N+1 funcionando correctamente!")
    else:
        print("⚠️  Posible problema de N+1 queries")
        
    # Mostrar ejemplo de agrupación
    print(f"\n📋 Ejemplo de agrupación:")
    grouped_data = {}
    for item in result_list:
        if item.producto.name not in grouped_data:
            grouped_data[item.producto.name] = []
        grouped_data[item.producto.name].append({
            'tipo_criticidad': item.relacion_tipo_criticidad.tipo_criticidad.name,
            'criticidad': item.relacion_tipo_criticidad.criticidad.name
        })
    
    for producto_name, combinaciones in grouped_data.items():
        print(f"   • {producto_name} ({len(combinaciones)} combinación{'es' if len(combinaciones) > 1 else ''})")
        for combo in combinaciones:
            print(f"     - {combo['tipo_criticidad']} / {combo['criticidad']}")
    
    return True

def crear_datos_ejemplo():
    """Crear algunos datos de ejemplo para probar la agrupación"""
    
    print("\n🔧 Creando datos de ejemplo...")
    
    # Crear productos
    producto1, _ = Producto.objects.get_or_create(name="Bomba Centrífuga")
    producto2, _ = Producto.objects.get_or_create(name="Válvula de Control")
    producto3, _ = Producto.objects.get_or_create(name="Compresor Rotativo")
    
    # Crear tipos de criticidad y criticidades
    tipo_crit1, _ = TipoCriticidad.objects.get_or_create(name="Operacional")
    tipo_crit2, _ = TipoCriticidad.objects.get_or_create(name="Seguridad")
    
    crit1, _ = Criticidad.objects.get_or_create(name="Alta")
    crit2, _ = Criticidad.objects.get_or_create(name="Media")
    crit3, _ = Criticidad.objects.get_or_create(name="Baja")
    
    # Crear relaciones tipo_criticidad-criticidad
    rel1, _ = TipoCriticidadCriticidad.objects.get_or_create(
        tipo_criticidad=tipo_crit1, 
        criticidad=crit1
    )
    rel2, _ = TipoCriticidadCriticidad.objects.get_or_create(
        tipo_criticidad=tipo_crit1, 
        criticidad=crit2
    )
    rel3, _ = TipoCriticidadCriticidad.objects.get_or_create(
        tipo_criticidad=tipo_crit2, 
        criticidad=crit1
    )
    rel4, _ = TipoCriticidadCriticidad.objects.get_or_create(
        tipo_criticidad=tipo_crit2, 
        criticidad=crit3
    )
    
    # Crear múltiples relaciones para cada producto (para probar agrupación)
    # Producto 1 - múltiples combinaciones
    ProductoTipoCritCrit.objects.get_or_create(
        producto=producto1, 
        relacion_tipo_criticidad=rel1
    )
    ProductoTipoCritCrit.objects.get_or_create(
        producto=producto1, 
        relacion_tipo_criticidad=rel2
    )
    ProductoTipoCritCrit.objects.get_or_create(
        producto=producto1, 
        relacion_tipo_criticidad=rel3
    )
    
    # Producto 2 - múltiples combinaciones
    ProductoTipoCritCrit.objects.get_or_create(
        producto=producto2, 
        relacion_tipo_criticidad=rel1
    )
    ProductoTipoCritCrit.objects.get_or_create(
        producto=producto2, 
        relacion_tipo_criticidad=rel4
    )
    
    # Producto 3 - una sola combinación
    ProductoTipoCritCrit.objects.get_or_create(
        producto=producto3, 
        relacion_tipo_criticidad=rel2
    )
    
    print("✅ Datos de ejemplo creados correctamente!")

if __name__ == "__main__":
    print("🧪 Script de verificación de tabla agrupada de productos")
    print("=" * 60)
    
    # Verificar datos existentes
    verificar_datos_productos()
    
    # Crear datos de ejemplo si es necesario
    crear_datos_ejemplo()
    
    # Verificar nuevamente
    print("\n" + "=" * 60)
    verificar_datos_productos()
    
    print("\n✅ ¡Verificación completa!")
    print("\n💡 Para ver la tabla agrupada:")
    print("   1. Ejecutar: python manage.py runserver")
    print("   2. Abrir: http://localhost:8000/complementos/productos/")
    print("   3. Verificar que los productos con múltiples combinaciones se agrupen correctamente")
