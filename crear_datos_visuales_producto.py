#!/usr/bin/env python3
"""
Script para crear datos de prueba visuales para la eliminación en cascada de productos.
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

def crear_datos_visuales():
    """Crear datos de prueba para visualizar la eliminación en cascada."""
    print("🎨 Creando datos de prueba visuales para eliminación en cascada de productos...")
    
    with transaction.atomic():
        # Limpiar datos existentes
        Tecnologia.objects.all().delete()
        TipoEquipo.objects.all().delete()
        Producto.objects.all().delete()
        TipoCriticidadCriticidad.objects.all().delete()
        TipoCriticidad.objects.all().delete()
        Criticidad.objects.all().delete()
        
        # Crear criticidades
        crit_critica = Criticidad.objects.create(name="Crítica")
        crit_alta = Criticidad.objects.create(name="Alta")
        crit_media = Criticidad.objects.create(name="Media")
        
        # Crear tipos de criticidad
        tipo_seguridad = TipoCriticidad.objects.create(name="Seguridad")
        tipo_rendimiento = TipoCriticidad.objects.create(name="Rendimiento")
        tipo_disponibilidad = TipoCriticidad.objects.create(name="Disponibilidad")
        
        # Crear relaciones tipo-criticidad
        rel_seg_critica = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_seguridad,
            criticidad=crit_critica
        )
        rel_seg_media = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_seguridad,
            criticidad=crit_media
        )
        rel_rend_alta = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_rendimiento,
            criticidad=crit_alta
        )
        rel_disp_critica = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_disponibilidad,
            criticidad=crit_critica
        )
        
        # Crear productos
        prod_eliminable = Producto.objects.create(name="ProdTest Eliminable")
        prod_compartido = Producto.objects.create(name="ProdTest Compartido")
        prod_permanente = Producto.objects.create(name="ProdTest Permanente")
        
        # Crear relaciones producto-tipo-criticidad
        # Producto Eliminable - Solo tiene 1 relación
        rel_p_eliminable = ProductoTipoCritCrit.objects.create(
            producto=prod_eliminable,
            relacion_tipo_criticidad=rel_seg_critica
        )
        
        # Producto Compartido - Tiene 2 relaciones
        rel_p_compartido1 = ProductoTipoCritCrit.objects.create(
            producto=prod_compartido,
            relacion_tipo_criticidad=rel_seg_media
        )
        rel_p_compartido2 = ProductoTipoCritCrit.objects.create(
            producto=prod_compartido,
            relacion_tipo_criticidad=rel_rend_alta
        )
        
        # Producto Permanente - Tiene 1 relación
        rel_p_permanente = ProductoTipoCritCrit.objects.create(
            producto=prod_permanente,
            relacion_tipo_criticidad=rel_disp_critica
        )
        
        # Crear tipos de equipo
        eq_solo = TipoEquipo.objects.create(name="EquipoTest Solo")
        eq_compartido = TipoEquipo.objects.create(name="EquipoTest Compartido")
        eq_permanente = TipoEquipo.objects.create(name="EquipoTest Permanente")
        
        # Crear relaciones tipo-equipo-producto
        # Equipo Solo - Solo usado por producto eliminable
        rel_eq_solo = TipoEquipoProducto.objects.create(
            tipo_equipo=eq_solo,
            relacion_producto=rel_p_eliminable
        )
        
        # Equipo Compartido - Usado por producto eliminable y compartido
        rel_eq_compartido1 = TipoEquipoProducto.objects.create(
            tipo_equipo=eq_compartido,
            relacion_producto=rel_p_eliminable
        )
        rel_eq_compartido2 = TipoEquipoProducto.objects.create(
            tipo_equipo=eq_compartido,
            relacion_producto=rel_p_compartido1
        )
        
        # Equipo Permanente - Usado por producto compartido y permanente
        rel_eq_permanente1 = TipoEquipoProducto.objects.create(
            tipo_equipo=eq_permanente,
            relacion_producto=rel_p_compartido2
        )
        rel_eq_permanente2 = TipoEquipoProducto.objects.create(
            tipo_equipo=eq_permanente,
            relacion_producto=rel_p_permanente
        )
        
        # Crear tecnologías
        tech_solo = Tecnologia.objects.create(name="TechTest Solo")
        tech_compartido = Tecnologia.objects.create(name="TechTest Compartido")
        tech_permanente = Tecnologia.objects.create(name="TechTest Permanente")
        
        # Crear relaciones tecnología-tipo-equipo
        # Tecnología Solo - Solo usada por equipo que será eliminado
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech_solo,
            relacion_tipo_equipo=rel_eq_solo
        )
        
        # Tecnología Compartida - Usada por equipo que será eliminado y uno que no
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech_compartido,
            relacion_tipo_equipo=rel_eq_solo
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech_compartido,
            relacion_tipo_equipo=rel_eq_compartido2
        )
        
        # Tecnología Permanente - Usada por equipos que se mantendrán
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech_permanente,
            relacion_tipo_equipo=rel_eq_permanente1
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech_permanente,
            relacion_tipo_equipo=rel_eq_permanente2
        )
        
    print("✅ Datos de prueba visuales creados exitosamente")
    print("\n📊 Resumen de datos creados:")
    print(f"  📋 Productos: {Producto.objects.count()}")
    print(f"  📋 Tipos de Equipo: {TipoEquipo.objects.count()}")
    print(f"  📋 Tecnologías: {Tecnologia.objects.count()}")
    print(f"  📋 Relaciones Producto-TipoCrit: {ProductoTipoCritCrit.objects.count()}")
    print(f"  📋 Relaciones TipoEquipo-Producto: {TipoEquipoProducto.objects.count()}")
    print(f"  📋 Relaciones Tecnología-TipoEquipo: {TecnologiaTipoEquipo.objects.count()}")
    
    print("\n🎯 Casos de prueba disponibles:")
    print("   1. Eliminar 'ProdTest Eliminable' completo:")
    print("      - Eliminará: EquipoTest Solo, TechTest Solo")
    print("      - Mantendrá: EquipoTest Compartido, TechTest Compartido")
    print("      - Mantendrá: EquipoTest Permanente, TechTest Permanente")
    print()
    print("   2. Eliminar solo relación 'ProdTest Compartido - Seguridad - Media':")
    print("      - Mantendrá: ProdTest Compartido (tendrá relación con Rendimiento)")
    print("      - Actualizará: EquipoTest Compartido (perderá 1 relación)")
    print("      - Mantendrá: todas las tecnologías")
    print()
    print("   3. Eliminar 'ProdTest Compartido' completo:")
    print("      - Eliminará: EquipoTest Compartido si no tiene más relaciones")
    print("      - Mantendrá: EquipoTest Permanente, TechTest Permanente")
    
    print("\n🌐 Navega a: http://127.0.0.1:8000/complementos/productos/")
    print("🧪 Prueba los botones de eliminar en las filas de ProdTest")

if __name__ == "__main__":
    crear_datos_visuales()
