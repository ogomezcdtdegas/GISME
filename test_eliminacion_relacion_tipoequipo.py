#!/usr/bin/env python3
"""
Script de prueba para verificar la eliminación en cascada de relaciones específicas de tipos de equipo.
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
        tipo_eq1 = TipoEquipo.objects.create(name="TipoEquipo Multi")
        tipo_eq2 = TipoEquipo.objects.create(name="TipoEquipo Solo")
        
        # Crear relaciones tipo-equipo-producto
        # TipoEquipo Multi usado por ambas relaciones de producto1 y producto2
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
        # TipoEquipo Solo usado solo por primera relación de producto1
        rel_te4 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_eq2,
            relacion_producto=rel_p1
        )
        
        # Crear tecnologías
        tech1 = Tecnologia.objects.create(name="Tecnología Multi")
        tech2 = Tecnologia.objects.create(name="Tecnología Solo")
        
        # Crear relaciones tecnología-tipo-equipo
        # Tecnología Multi usada por varios tipos de equipo
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=rel_te1
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=rel_te2
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=rel_te3
        )
        # Tecnología Solo usada solo por relación que puede ser eliminada
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech2,
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

def test_eliminar_relacion_especifica():
    """Prueba eliminar una relación específica de un tipo de equipo con múltiples relaciones."""
    print("\n🧪 Test: Eliminar relación específica (TipoEquipo Multi - primera relación)")
    
    # Buscar primera relación de TipoEquipo Multi
    tipo_eq_multi = TipoEquipo.objects.get(name="TipoEquipo Multi")
    primera_relacion = TipoEquipoProducto.objects.filter(
        tipo_equipo=tipo_eq_multi,
        relacion_producto__producto__name="Producto Multi"
    ).first()
    
    print(f"  Eliminando relación: {primera_relacion}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - TipoEquipo Multi tiene {TipoEquipoProducto.objects.filter(tipo_equipo=tipo_eq_multi).count()} relaciones")
    print(f"    - Tecnología Multi tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Tecnología Multi').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_TipoEquipo.Commands.DeleteTipoEquipoCommand.DeleteTipoEquipoCommand import DeleteTipoEquipoRelacionCommand
    
    class MockRequest:
        pass
    
    command = DeleteTipoEquipoRelacionCommand()
    response = command.delete(MockRequest(), primera_relacion.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - TipoEquipo Multi existe: {TipoEquipo.objects.filter(name='TipoEquipo Multi').exists()}")
    print(f"    - TipoEquipo Multi tiene {TipoEquipoProducto.objects.filter(tipo_equipo__name='TipoEquipo Multi').count()} relaciones")
    print(f"    - Tecnología Multi existe: {Tecnologia.objects.filter(name='Tecnología Multi').exists()}")
    
    mostrar_estado_actual()

def test_eliminar_ultima_relacion():
    """Prueba eliminar la última relación de un tipo de equipo."""
    print("\n🧪 Test: Eliminar última relación (TipoEquipo Solo)")
    
    # Buscar la relación del TipoEquipo Solo
    tipo_eq_solo = TipoEquipo.objects.get(name="TipoEquipo Solo")
    relacion_solo = TipoEquipoProducto.objects.filter(tipo_equipo=tipo_eq_solo).first()
    
    print(f"  Eliminando última relación: {relacion_solo}")
    
    # Información antes de eliminar
    print("  Estado antes de eliminar:")
    print(f"    - TipoEquipo Solo tiene {TipoEquipoProducto.objects.filter(tipo_equipo=tipo_eq_solo).count()} relaciones")
    print(f"    - Tecnología Solo tiene {TecnologiaTipoEquipo.objects.filter(tecnologia__name='Tecnología Solo').count()} relaciones")
    
    # Eliminar usando el comando
    from _AppComplementos.views.views_TipoEquipo.Commands.DeleteTipoEquipoCommand.DeleteTipoEquipoCommand import DeleteTipoEquipoRelacionCommand
    
    class MockRequest:
        pass
    
    command = DeleteTipoEquipoRelacionCommand()
    response = command.delete(MockRequest(), relacion_solo.id)
    
    print(f"  Resultado: {'✅ Éxito' if response.data.get('success') else '❌ Error'}")
    print(f"  Mensaje: {response.data.get('message', '')}")
    
    # Verificar estado después
    print("\n  Estado después de eliminar:")
    print(f"    - TipoEquipo Solo existe: {TipoEquipo.objects.filter(name='TipoEquipo Solo').exists()}")
    print(f"    - Tecnología Solo existe: {Tecnologia.objects.filter(name='Tecnología Solo').exists()}")
    
    mostrar_estado_actual()

def main():
    """Función principal."""
    print("🚀 Iniciando pruebas de eliminación en cascada de relaciones de tipos de equipo\n")
    
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
