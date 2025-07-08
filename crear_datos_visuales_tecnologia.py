#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Crear datos de prueba visuales para eliminación en cascada de tecnologías
"""

import os
import sys
import django

# Configure Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import *

def clean_and_create_visual_data():
    """Clean and create visual test data for technology cascade deletion"""
    
    print("🧹 Cleaning existing data...")
    TecnologiaTipoEquipo.objects.all().delete()
    Tecnologia.objects.all().delete()
    TipoEquipoProducto.objects.all().delete()
    TipoEquipo.objects.all().delete()
    ProductoTipoCritCrit.objects.all().delete()
    Producto.objects.all().delete()
    TipoCriticidadCriticidad.objects.all().delete()
    Criticidad.objects.all().delete()
    TipoCriticidad.objects.all().delete()
    
    print("📦 Creating visual test data for technology cascade deletion...")
    
    # Create base data
    tipo_crit = TipoCriticidad.objects.create(name="TipoCrit Visual")
    criticidad = Criticidad.objects.create(name="Criticidad Visual")
    tipo_crit_rel = TipoCriticidadCriticidad.objects.create(
        tipo_criticidad=tipo_crit,
        criticidad=criticidad
    )
    
    # Create products
    producto_a = Producto.objects.create(name="ProdTest A")
    producto_b = Producto.objects.create(name="ProdTest B")
    
    # Create product relations
    prod_rel_a = ProductoTipoCritCrit.objects.create(
        producto=producto_a,
        relacion_tipo_criticidad=tipo_crit_rel
    )
    prod_rel_b = ProductoTipoCritCrit.objects.create(
        producto=producto_b,
        relacion_tipo_criticidad=tipo_crit_rel
    )
    
    # Create equipment types
    equipo_eliminable = TipoEquipo.objects.create(name="EquipoTest Eliminable")
    equipo_compartido = TipoEquipo.objects.create(name="EquipoTest Compartido")
    equipo_permanente = TipoEquipo.objects.create(name="EquipoTest Permanente")
    
    # Create equipment relations
    equipo_rel_1 = TipoEquipoProducto.objects.create(
        tipo_equipo=equipo_eliminable,
        relacion_producto=prod_rel_a
    )
    equipo_rel_2 = TipoEquipoProducto.objects.create(
        tipo_equipo=equipo_compartido,
        relacion_producto=prod_rel_a
    )
    equipo_rel_3 = TipoEquipoProducto.objects.create(
        tipo_equipo=equipo_compartido,
        relacion_producto=prod_rel_b
    )
    equipo_rel_4 = TipoEquipoProducto.objects.create(
        tipo_equipo=equipo_permanente,
        relacion_producto=prod_rel_b
    )
    
    # Create technologies
    tech_eliminable = Tecnologia.objects.create(name="TechTest Eliminable")
    tech_compartida = Tecnologia.objects.create(name="TechTest Compartida")
    tech_permanente = Tecnologia.objects.create(name="TechTest Permanente")
    
    # Create technology relations
    # Technology 1: Only relation with eliminable equipment
    tech_rel_1 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tech_eliminable,
        relacion_tipo_equipo=equipo_rel_1
    )
    
    # Technology 2: Multiple relations with shared equipment
    tech_rel_2 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tech_compartida,
        relacion_tipo_equipo=equipo_rel_2
    )
    tech_rel_3 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tech_compartida,
        relacion_tipo_equipo=equipo_rel_3
    )
    
    # Technology 3: Only relation with permanent equipment
    tech_rel_4 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tech_permanente,
        relacion_tipo_equipo=equipo_rel_4
    )
    
    # Add one more relation to make it more interesting
    tech_rel_5 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tech_permanente,
        relacion_tipo_equipo=equipo_rel_2
    )
    
    # Count data
    print("✅ Visual test data created successfully")
    print(f"\n📊 Summary of created data:")
    print(f"  📋 Products: {Producto.objects.count()}")
    print(f"  📋 Equipment Types: {TipoEquipo.objects.count()}")
    print(f"  📋 Technologies: {Tecnologia.objects.count()}")
    print(f"  📋 Product-Criticidad relations: {ProductoTipoCritCrit.objects.count()}")
    print(f"  📋 Equipment-Product relations: {TipoEquipoProducto.objects.count()}")
    print(f"  📋 Technology-Equipment relations: {TecnologiaTipoEquipo.objects.count()}")
    
    print(f"\n🎯 Test cases available:")
    print(f"   1. Delete 'TechTest Eliminable' complete:")
    print(f"      - Will delete: TechTest Eliminable")
    print(f"      - Will keep: TechTest Compartida, TechTest Permanente")
    print(f"")
    print(f"   2. Delete only relation 'TechTest Compartida - EquipoTest Compartido (ProdTest A)':")
    print(f"      - Will keep: TechTest Compartida (has relation with ProdTest B)")
    print(f"      - Will update: TechTest Compartida (loses 1 relation)")
    print(f"")
    print(f"   3. Delete 'TechTest Compartida' complete:")
    print(f"      - Will delete: TechTest Compartida and all its relations")
    print(f"      - Will keep: TechTest Eliminable, TechTest Permanente")
    print(f"")
    print(f"   4. Delete only relation 'TechTest Permanente - EquipoTest Compartido (ProdTest A)':")
    print(f"      - Will keep: TechTest Permanente (has relation with EquipoTest Permanente)")
    print(f"      - Will update: TechTest Permanente (loses 1 relation)")
    
    print(f"\n🌐 Navigate to: http://127.0.0.1:8000/complementos/tecnologias/")
    print(f"🧪 Test the delete buttons on TechTest rows")

if __name__ == "__main__":
    clean_and_create_visual_data()
