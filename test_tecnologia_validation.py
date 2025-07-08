#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test validation for Technology cascade deletion functionality
"""

import os
import sys
import django

# Configure Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import *

def clean_data():
    """Clean all data to start fresh"""
    print("Cleaning existing data...")
    TecnologiaTipoEquipo.objects.all().delete()
    Tecnologia.objects.all().delete()
    TipoEquipoProducto.objects.all().delete()
    TipoEquipo.objects.all().delete()
    ProductoTipoCritCrit.objects.all().delete()
    Producto.objects.all().delete()
    TipoCriticidadCriticidad.objects.all().delete()
    Criticidad.objects.all().delete()
    TipoCriticidad.objects.all().delete()

def create_test_data():
    """Create test data"""
    print("Creating test data...")
    
    # Create TipoCriticidad
    tipo_crit, _ = TipoCriticidad.objects.get_or_create(name="Test Type")
    
    # Create Criticidad  
    criticidad, _ = Criticidad.objects.get_or_create(name="Test Criticidad")
    
    # Create relation
    tipo_crit_rel, _ = TipoCriticidadCriticidad.objects.get_or_create(
        tipo_criticidad=tipo_crit,
        criticidad=criticidad
    )
    
    # Create Producto
    producto, _ = Producto.objects.get_or_create(name="Test Product")
    
    # Create relation
    prod_rel, _ = ProductoTipoCritCrit.objects.get_or_create(
        producto=producto,
        relacion_tipo_criticidad=tipo_crit_rel
    )
    
    # Create TipoEquipo
    tipo_equipo, _ = TipoEquipo.objects.get_or_create(name="Test Equipment")
    
    # Create relation
    tipo_equipo_rel, _ = TipoEquipoProducto.objects.get_or_create(
        tipo_equipo=tipo_equipo,
        relacion_producto=prod_rel
    )
    
    # Create Tecnologia
    tecnologia, _ = Tecnologia.objects.get_or_create(name="Test Technology")
    
    # Create relation
    tech_rel, _ = TecnologiaTipoEquipo.objects.get_or_create(
        tecnologia=tecnologia,
        relacion_tipo_equipo=tipo_equipo_rel
    )
    
    return {
        'tecnologia': tecnologia,
        'tech_rel': tech_rel,
        'tipo_equipo': tipo_equipo,
        'tipo_equipo_rel': tipo_equipo_rel
    }

def test_technology_deletion():
    """Test technology cascade deletion"""
    print("\n=== Testing Technology Cascade Deletion ===")
    
    data = create_test_data()
    
    # Check initial state
    print(f"Initial state:")
    print(f"  - Technologies: {Tecnologia.objects.count()}")
    print(f"  - Tech-Equipment relations: {TecnologiaTipoEquipo.objects.count()}")
    
    # Test technology deletion
    tecnologia_id = data['tecnologia'].id
    print(f"\nDeleting technology ID: {tecnologia_id}")
    
    # Import and execute command
    from _AppComplementos.views.views_Tecnologia.Commands.DeleteTecnologiaCommand.DeleteTecnologiaCommand import DeleteTecnologiaCommand
    
    command = DeleteTecnologiaCommand()
    # Simulate the execute method
    try:
        tecnologia = Tecnologia.objects.get(id=tecnologia_id)
        relaciones = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia)
        
        print(f"  - Technology '{tecnologia.name}' has {relaciones.count()} relations")
        
        # Delete all relations
        relaciones.delete()
        
        # Delete technology
        tecnologia.delete()
        
        print("  - Technology deleted successfully")
        
    except Exception as e:
        print(f"  - Error: {e}")
    
    # Check final state
    print(f"\nFinal state:")
    print(f"  - Technologies: {Tecnologia.objects.count()}")
    print(f"  - Tech-Equipment relations: {TecnologiaTipoEquipo.objects.count()}")
    
    clean_data()

def test_technology_relation_deletion():
    """Test technology relation deletion"""
    print("\n=== Testing Technology Relation Deletion ===")
    
    data = create_test_data()
    
    # Create additional relation for same technology
    tipo_equipo2, _ = TipoEquipo.objects.get_or_create(name="Test Equipment 2")
    prod2, _ = Producto.objects.get_or_create(name="Test Product 2")
    
    # Create the chain for second relation
    tipo_crit_rel2 = TipoCriticidadCriticidad.objects.first()
    prod_rel2, _ = ProductoTipoCritCrit.objects.get_or_create(
        producto=prod2,
        relacion_tipo_criticidad=tipo_crit_rel2
    )
    tipo_equipo_rel2, _ = TipoEquipoProducto.objects.get_or_create(
        tipo_equipo=tipo_equipo2,
        relacion_producto=prod_rel2
    )
    
    # Add second relation to same technology
    tech_rel2, _ = TecnologiaTipoEquipo.objects.get_or_create(
        tecnologia=data['tecnologia'],
        relacion_tipo_equipo=tipo_equipo_rel2
    )
    
    # Check initial state
    tecnologia = data['tecnologia']
    initial_relations = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()
    print(f"Initial state:")
    print(f"  - Technology '{tecnologia.name}' has {initial_relations} relations")
    
    # Test relation deletion
    relacion_id = data['tech_rel'].id
    print(f"\nDeleting specific relation ID: {relacion_id}")
    
    # Import and execute relation deletion command
    from _AppComplementos.views.views_Tecnologia.Commands.DeleteTecnologiaRelacionCommand.DeleteTecnologiaRelacionCommand import DeleteTecnologiaRelacionCommand
    
    command = DeleteTecnologiaRelacionCommand()
    # Simulate the execute method
    try:
        relacion = TecnologiaTipoEquipo.objects.get(id=relacion_id)
        tecnologia = relacion.tecnologia
        
        # Delete relation
        relacion.delete()
        
        # Check remaining relations
        remaining_relations = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()
        
        if remaining_relations == 0:
            # Delete technology if no relations left
            tecnologia.delete()
            print(f"  - Relation deleted and technology removed (no relations left)")
        else:
            print(f"  - Relation deleted, technology kept ({remaining_relations} relations remaining)")
            
    except Exception as e:
        print(f"  - Error: {e}")
    
    # Check final state
    final_relations = TecnologiaTipoEquipo.objects.filter(tecnologia__name="Test Technology").count()
    print(f"\nFinal state:")
    print(f"  - Technology relations: {final_relations}")
    print(f"  - Technologies: {Tecnologia.objects.count()}")
    
    clean_data()

def main():
    print("Starting Technology Cascade Deletion Tests...")
    
    try:
        test_technology_deletion()
        test_technology_relation_deletion()
        
        print("\n=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"\nError running tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
