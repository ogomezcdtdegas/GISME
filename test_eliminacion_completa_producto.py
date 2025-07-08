#!/usr/bin/env python3
"""
Script de prueba para verificar la eliminación en cascada de productos.
Verifica que se eliminen correctamente los tipos de equipo y tecnologías huérfanas.
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
        tipo_eq1 = TipoEquipo.objects.create(name="Servidor")
        tipo_eq2 = TipoEquipo.objects.create(name="Workstation")
        tipo_eq3 = TipoEquipo.objects.create(name="Router")
        
        # Crear relaciones tipo-equipo-producto
        # tipo_eq1 (Servidor) usado por producto1 y producto2
        rel_te1 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq1,
            relacion_producto=rel_p1
        )
        rel_te2 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq1,
            relacion_producto=rel_p2
        )
        # tipo_eq2 (Workstation) usado solo por producto1
        rel_te3 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq2,
            relacion_producto=rel_p1
        )
        # tipo_eq3 (Router) usado solo por producto3
        rel_te4 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq3,
            relacion_producto=rel_p3
        )
        
        # Crear tecnologías
        tech1 = Tecnologia.objects.create(name="Java")
        tech2 = Tecnologia.objects.create(name="Python")
        tech3 = Tecnologia.objects.create(name="Docker")
        
        # Crear relaciones tecnología-tipo-equipo
        # tech1 (Java) usado por tipo_eq1 y tipo_eq2
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=rel_te1
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=rel_te3
        )
        # tech2 (Python) usado solo por tipo_eq1
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech2,
            relacion_tipo_equipo=rel_te2
        )
        # tech3 (Docker) usado solo por tipo_eq3
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
    
    print("\n🔍 Detalle de productos:")
    for producto in Producto.objects.all():
        relaciones = ProductoTipoCritCrit.objects.filter(producto=producto).count()
        print(f"  • {producto.name}: {relaciones} relaciones")

def test_eliminar_producto_completo():
    """Prueba eliminar un producto completo."""
    print("\n🧪 Test: Eliminar producto completo")
    
    # Buscar producto A
    producto_a = Producto.objects.get(name="Producto A")
    print(f"  Eliminando producto: {producto_a.name}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - Tipo Workstation tiene {TipoEquipoProducto.objects.filter(tipo_equipo__name='Workstation').count()} relaciones")
    print(f"    - Tecnología Java tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Java').count()} relaciones")
    print(f"    - Tipo Servidor tiene {TipoEquipoProducto.objects.filter(tipo_equipo__name='Servidor').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_Producto.Commands.DeleteProductoCommand.DeleteProductoCommand import DeleteProductoCommand
    
    class MockRequest:
        pass
    
    command = DeleteProductoCommand()
    response = command.delete(MockRequest(), producto_a.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - Producto A existe: {Producto.objects.filter(name='Producto A').exists()}")
    print(f"    - Tipo Workstation existe: {TipoEquipo.objects.filter(name='Workstation').exists()}")
    print(f"    - Tecnología Java existe: {Tecnologia.objects.filter(name='Java').exists()}")
    print(f"    - Tipo Servidor existe: {TipoEquipo.objects.filter(name='Servidor').exists()}")
    
    mostrar_estado_actual()

def test_eliminar_producto_con_relaciones_compartidas():
    """Prueba eliminar un producto que comparte relaciones."""
    print("\n🧪 Test: Eliminar producto con relaciones compartidas")
    
    # Buscar producto B
    producto_b = Producto.objects.get(name="Producto B")
    print(f"  Eliminando producto: {producto_b.name}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - Tipo Servidor tiene {TipoEquipoProducto.objects.filter(tipo_equipo__name='Servidor').count()} relaciones")
    print(f"    - Tecnología Python tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Python').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_Producto.Commands.DeleteProductoCommand.DeleteProductoCommand import DeleteProductoCommand
    
    class MockRequest:
        pass
    
    command = DeleteProductoCommand()
    response = command.delete(MockRequest(), producto_b.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - Producto B existe: {Producto.objects.filter(name='Producto B').exists()}")
    print(f"    - Tipo Servidor existe: {TipoEquipo.objects.filter(name='Servidor').exists()}")
    print(f"    - Tecnología Python existe: {Tecnologia.objects.filter(name='Python').exists()}")
    
    mostrar_estado_actual()

def test_eliminar_producto_huerfano():
    """Prueba eliminar un producto que dejará huérfanos."""
    print("\n🧪 Test: Eliminar producto que dejará huérfanos")
    
    # Buscar producto C
    producto_c = Producto.objects.get(name="Producto C")
    print(f"  Eliminando producto: {producto_c.name}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - Tipo Router tiene {TipoEquipoProducto.objects.filter(tipo_equipo__name='Router').count()} relaciones")
    print(f"    - Tecnología Docker tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Docker').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_Producto.Commands.DeleteProductoCommand.DeleteProductoCommand import DeleteProductoCommand
    
    class MockRequest:
        pass
    
    command = DeleteProductoCommand()
    response = command.delete(MockRequest(), producto_c.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - Producto C existe: {Producto.objects.filter(name='Producto C').exists()}")
    print(f"    - Tipo Router existe: {TipoEquipo.objects.filter(name='Router').exists()}")
    print(f"    - Tecnología Docker existe: {Tecnologia.objects.filter(name='Docker').exists()}")
    
    mostrar_estado_actual()

def main():
    """Función principal."""
    print("🚀 Iniciando pruebas de eliminación en cascada de productos\n")
    
    try:
        crear_datos_prueba()
        test_eliminar_producto_completo()
        test_eliminar_producto_con_relaciones_compartidas()
        test_eliminar_producto_huerfano()
        
        print("\n🎉 Todas las pruebas completadas")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
