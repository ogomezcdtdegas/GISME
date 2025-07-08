#!/usr/bin/env python3
"""
Script de prueba para verificar la eliminación en cascada de tipos de equipo.
Verifica que se eliminen correctamente las tecnologías huérfanas.
"""

import os
import sys
import django
from django.db import transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import (
    Criticidad, TipoCriticidad, TipoCriticidadCriticidad,
    Producto, ProductoTipoCritCrit,
    TipoEquipo, TipoEquipoProducto,
    Tecnologia, TecnologiaTipoEquipo
)

def crear_datos_prueba():
    """Crear datos de prueba para verificar la eliminación en cascada."""
    print("🔄 Creando datos de prueba...")
    
    with transaction.atomic():
        # Limpiar datos existentes
        Tecnologia.objects.all().delete()
        TipoEquipo.objects.all().delete()
        Producto.objects.all().delete()
        TipoCriticidadCriticidad.objects.all().delete()
        TipoCriticidad.objects.all().delete()
        Criticidad.objects.all().delete()
        
        # Crear criticidades
        criticidad1 = Criticidad.objects.create(name="Crítica")
        criticidad2 = Criticidad.objects.create(name="Alta")
        
        # Crear tipos de criticidad
        tipo_crit1 = TipoCriticidad.objects.create(name="Seguridad")
        tipo_crit2 = TipoCriticidad.objects.create(name="Rendimiento")
        
        # Crear relaciones tipo-criticidad
        rel_tc1 = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_crit1,
            criticidad=criticidad1
        )
        rel_tc2 = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_crit2,
            criticidad=criticidad2
        )
        
        # Crear productos
        producto1 = Producto.objects.create(name="Producto A")
        producto2 = Producto.objects.create(name="Producto B")
        producto3 = Producto.objects.create(name="Producto C")
        
        # Crear relaciones producto-tipo-criticidad
        rel_p1 = ProductoTipoCritCrit.objects.create(
            producto=producto1,
            relacion_tipo_criticidad=rel_tc1
        )
        rel_p2 = ProductoTipoCritCrit.objects.create(
            producto=producto2,
            relacion_tipo_criticidad=rel_tc2
        )
        rel_p3 = ProductoTipoCritCrit.objects.create(
            producto=producto3,
            relacion_tipo_criticidad=rel_tc1
        )
        
        # Crear tipos de equipo
        tipo_eq1 = TipoEquipo.objects.create(name="TipoEquipo A")
        tipo_eq2 = TipoEquipo.objects.create(name="TipoEquipo B")
        tipo_eq3 = TipoEquipo.objects.create(name="TipoEquipo C")
        
        # Crear relaciones tipo-equipo-producto
        # tipo_eq1 usado por producto1 y producto2
        rel_te1 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq1,
            relacion_producto=rel_p1
        )
        rel_te2 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq1,
            relacion_producto=rel_p2
        )
        # tipo_eq2 usado solo por producto1
        rel_te3 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq2,
            relacion_producto=rel_p1
        )
        # tipo_eq3 usado solo por producto3
        rel_te4 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq3,
            relacion_producto=rel_p3
        )
        
        # Crear tecnologías
        tech1 = Tecnologia.objects.create(name="Tecnología A")
        tech2 = Tecnologia.objects.create(name="Tecnología B")
        tech3 = Tecnologia.objects.create(name="Tecnología C")
        
        # Crear relaciones tecnología-tipo-equipo
        # tech1 usado por tipo_eq1 y tipo_eq2
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=rel_te1
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=rel_te3
        )
        # tech2 usado solo por tipo_eq1
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech2,
            relacion_tipo_equipo=rel_te2
        )
        # tech3 usado solo por tipo_eq3
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech3,
            relacion_tipo_equipo=rel_te4
        )
        
    print("✅ Datos de prueba creados exitosamente")
    mostrar_estado_actual()

def mostrar_estado_actual():
    """Mostrar el estado actual de la base de datos."""
    print("\n📊 Estado actual de la base de datos:")
    print(f"  • Productos: {Producto.objects.count()}")
    print(f"  • Tipos de Equipo: {TipoEquipo.objects.count()}")
    print(f"  • Tecnologías: {Tecnologia.objects.count()}")
    print(f"  • Relaciones Producto-TipoCrit: {ProductoTipoCritCrit.objects.count()}")
    print(f"  • Relaciones TipoEquipo-Producto: {TipoEquipoProducto.objects.count()}")
    print(f"  • Relaciones Tecnología-TipoEquipo: {TecnologiaTipoEquipo.objects.count()}")
    
    print("\n🔍 Detalle de tipos de equipo:")
    for tipo_eq in TipoEquipo.objects.all():
        relaciones = TipoEquipoProducto.objects.filter(tipo_equipo=tipo_eq).count()
        print(f"  • {tipo_eq.name}: {relaciones} relaciones")
    
    print("\n🔍 Detalle de tecnologías:")
    for tech in Tecnologia.objects.all():
        relaciones = TecnologiaTipoEquipo.objects.filter(tecnologia=tech).count()
        print(f"  • {tech.name}: {relaciones} relaciones")

def test_eliminar_tipo_equipo_completo():
    """Prueba eliminar un tipo de equipo completo."""
    print("\n🧪 Test: Eliminar tipo de equipo completo")
    
    # Buscar TipoEquipo A
    tipo_eq_a = TipoEquipo.objects.get(name="TipoEquipo A")
    print(f"  Eliminando tipo de equipo: {tipo_eq_a.name}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - Tecnología A tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Tecnología A').count()} relaciones")
    print(f"    - Tecnología B tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Tecnología B').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_TipoEquipo.Commands.DeleteTipoEquipoCommand.DeleteTipoEquipoCommand import DeleteTipoEquipoCommand
    
    class MockRequest:
        pass
    
    command = DeleteTipoEquipoCommand()
    response = command.delete(MockRequest(), tipo_eq_a.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - TipoEquipo A existe: {TipoEquipo.objects.filter(name='TipoEquipo A').exists()}")
    print(f"    - Tecnología A existe: {Tecnologia.objects.filter(name='Tecnología A').exists()}")
    print(f"    - Tecnología B existe: {Tecnologia.objects.filter(name='Tecnología B').exists()}")
    
    mostrar_estado_actual()

def test_eliminar_tipo_equipo_huerfano():
    """Prueba eliminar un tipo de equipo que dejará huérfanos."""
    print("\n🧪 Test: Eliminar tipo de equipo que dejará huérfanos")
    
    # Buscar TipoEquipo C
    tipo_eq_c = TipoEquipo.objects.get(name="TipoEquipo C")
    print(f"  Eliminando tipo de equipo: {tipo_eq_c.name}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - Tecnología C tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Tecnología C').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_TipoEquipo.Commands.DeleteTipoEquipoCommand.DeleteTipoEquipoCommand import DeleteTipoEquipoCommand
    
    class MockRequest:
        pass
    
    command = DeleteTipoEquipoCommand()
    response = command.delete(MockRequest(), tipo_eq_c.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - TipoEquipo C existe: {TipoEquipo.objects.filter(name='TipoEquipo C').exists()}")
    print(f"    - Tecnología C existe: {Tecnologia.objects.filter(name='Tecnología C').exists()}")
    
    mostrar_estado_actual()

def test_eliminar_tipo_equipo_compartido():
    """Prueba eliminar un tipo de equipo con dependencias compartidas."""
    print("\n🧪 Test: Eliminar tipo de equipo con dependencias compartidas")
    
    # Buscar TipoEquipo B
    tipo_eq_b = TipoEquipo.objects.get(name="TipoEquipo B")
    print(f"  Eliminando tipo de equipo: {tipo_eq_b.name}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - Tecnología A tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Tecnología A').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_TipoEquipo.Commands.DeleteTipoEquipoCommand.DeleteTipoEquipoCommand import DeleteTipoEquipoCommand
    
    class MockRequest:
        pass
    
    command = DeleteTipoEquipoCommand()
    response = command.delete(MockRequest(), tipo_eq_b.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - TipoEquipo B existe: {TipoEquipo.objects.filter(name='TipoEquipo B').exists()}")
    print(f"    - Tecnología A existe: {Tecnologia.objects.filter(name='Tecnología A').exists()}")
    
    mostrar_estado_actual()

def main():
    """Función principal."""
    print("🚀 Iniciando pruebas de eliminación en cascada de tipos de equipo\n")
    
    try:
        crear_datos_prueba()
        test_eliminar_tipo_equipo_completo()
        test_eliminar_tipo_equipo_huerfano()
        test_eliminar_tipo_equipo_compartido()
        
        print("\n🎉 Todas las pruebas completadas")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
