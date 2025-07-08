#!/usr/bin/env python3
"""
Script de prueba para verificar la eliminación en cascada de relaciones específicas de productos.
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
        criticidad3 = Criticidad.objects.create(name="Media")
        
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
        rel_tc3 = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_crit1,
            criticidad=criticidad3
        )
        
        # Crear productos
        producto1 = Producto.objects.create(name="Producto Multi")
        producto2 = Producto.objects.create(name="Producto Solo")
        
        # Crear relaciones producto-tipo-criticidad
        # Producto Multi tiene 2 relaciones
        rel_p1 = ProductoTipoCritCrit.objects.create(
            producto=producto1,
            relacion_tipo_criticidad=rel_tc1
        )
        rel_p2 = ProductoTipoCritCrit.objects.create(
            producto=producto1,
            relacion_tipo_criticidad=rel_tc3
        )
        # Producto Solo tiene 1 relación
        rel_p3 = ProductoTipoCritCrit.objects.create(
            producto=producto2,
            relacion_tipo_criticidad=rel_tc2
        )
        
        # Crear tipos de equipo
        tipo_eq1 = TipoEquipo.objects.create(name="Servidor")
        tipo_eq2 = TipoEquipo.objects.create(name="Workstation")
        tipo_eq3 = TipoEquipo.objects.create(name="Router")
        
        # Crear relaciones tipo-equipo-producto
        # tipo_eq1 (Servidor) usado por ambas relaciones de producto1 y producto2
        rel_te1 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq1,
            relacion_producto=rel_p1
        )
        rel_te2 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq1,
            relacion_producto=rel_p2
        )
        rel_te3 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq1,
            relacion_producto=rel_p3
        )
        # tipo_eq2 (Workstation) usado solo por primera relación de producto1
        rel_te4 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq2,
            relacion_producto=rel_p1
        )
        # tipo_eq3 (Router) usado solo por segunda relación de producto1
        rel_te5 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq3,
            relacion_producto=rel_p2
        )
        
        # Crear tecnologías
        tech1 = Tecnologia.objects.create(name="Java")
        tech2 = Tecnologia.objects.create(name="Python")
        tech3 = Tecnologia.objects.create(name="Docker")
        
        # Crear relaciones tecnología-tipo-equipo
        # tech1 (Java) usado por varios tipos de equipo
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=rel_te1
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=rel_te4
        )
        # tech2 (Python) usado solo por relación que se eliminará
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech2,
            relacion_tipo_equipo=rel_te4
        )
        # tech3 (Docker) usado solo por relación que se mantendrá
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech3,
            relacion_tipo_equipo=rel_te5
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
    
    print("\n🔍 Detalle de tipos de equipo:")
    for tipo_eq in TipoEquipo.objects.all():
        relaciones = TipoEquipoProducto.objects.filter(tipo_equipo=tipo_eq).count()
        print(f"  • {tipo_eq.name}: {relaciones} relaciones")

def test_eliminar_relacion_especifica():
    """Prueba eliminar una relación específica de un producto con múltiples relaciones."""
    print("\n🧪 Test: Eliminar relación específica (Producto Multi - primera relación)")
    
    # Buscar primera relación de Producto Multi
    producto_multi = Producto.objects.get(name="Producto Multi")
    primera_relacion = ProductoTipoCritCrit.objects.filter(
        producto=producto_multi,
        relacion_tipo_criticidad__criticidad__name="Crítica"
    ).first()
    
    print(f"  Eliminando relación: {primera_relacion}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - Producto Multi tiene {ProductoTipoCritCrit.objects.filter(producto=producto_multi).count()} relaciones")
    print(f"    - Tipo Workstation tiene {TipoEquipoProducto.objects.filter(tipo_equipo__name='Workstation').count()} relaciones")
    print(f"    - Tecnología Python tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Python').count()} relaciones")
    print(f"    - Tipo Servidor tiene {TipoEquipoProducto.objects.filter(tipo_equipo__name='Servidor').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_Producto.Commands.DeleteProductoRelacionCommand.DeleteProductoRelacionCommand import DeleteProductoRelacionCommand
    
    class MockRequest:
        pass
    
    command = DeleteProductoRelacionCommand()
    response = command.delete(MockRequest(), primera_relacion.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - Producto Multi existe: {Producto.objects.filter(name='Producto Multi').exists()}")
    print(f"    - Producto Multi tiene {ProductoTipoCritCrit.objects.filter(producto__name='Producto Multi').count()} relaciones")
    print(f"    - Tipo Workstation existe: {TipoEquipo.objects.filter(name='Workstation').exists()}")
    print(f"    - Tecnología Python existe: {Tecnologia.objects.filter(name='Python').exists()}")
    print(f"    - Tipo Servidor existe: {TipoEquipo.objects.filter(name='Servidor').exists()}")
    
    mostrar_estado_actual()

def test_eliminar_ultima_relacion():
    """Prueba eliminar la última relación de un producto."""
    print("\n🧪 Test: Eliminar última relación (Producto Solo)")
    
    # Buscar la relación del Producto Solo
    producto_solo = Producto.objects.get(name="Producto Solo")
    relacion_solo = ProductoTipoCritCrit.objects.filter(producto=producto_solo).first()
    
    print(f"  Eliminando última relación: {relacion_solo}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - Producto Solo tiene {ProductoTipoCritCrit.objects.filter(producto=producto_solo).count()} relaciones")
    print(f"    - Tipo Servidor tiene {TipoEquipoProducto.objects.filter(tipo_equipo__name='Servidor').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_Producto.Commands.DeleteProductoRelacionCommand.DeleteProductoRelacionCommand import DeleteProductoRelacionCommand
    
    class MockRequest:
        pass
    
    command = DeleteProductoRelacionCommand()
    response = command.delete(MockRequest(), relacion_solo.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - Producto Solo existe: {Producto.objects.filter(name='Producto Solo').exists()}")
    print(f"    - Tipo Servidor existe: {TipoEquipo.objects.filter(name='Servidor').exists()}")
    print(f"    - Tipo Servidor tiene {TipoEquipoProducto.objects.filter(tipo_equipo__name='Servidor').count()} relaciones")
    
    mostrar_estado_actual()

def main():
    """Función principal."""
    print("🚀 Iniciando pruebas de eliminación en cascada de relaciones de productos\n")
    
    try:
        crear_datos_prueba()
        test_eliminar_relacion_especifica()
        test_eliminar_ultima_relacion()
        
        print("\n🎉 Todas las pruebas completadas")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
