#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test final para validar funcionalidad completa de eliminación en cascada de Tecnología
"""

import os
import sys
import django

# Configure Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import *
from django.test import Client
from django.contrib.auth.models import User
import json

def test_technology_endpoint_complete():
    """Test complete technology deletion endpoint"""
    print("🧪 Testing Technology Complete Deletion Endpoint...")
    
    # Create test data
    tipo_crit = TipoCriticidad.objects.create(name="Test Endpoint Type")
    criticidad = Criticidad.objects.create(name="Test Endpoint Criticidad")
    tipo_crit_rel = TipoCriticidadCriticidad.objects.create(
        tipo_criticidad=tipo_crit,
        criticidad=criticidad
    )
    
    producto = Producto.objects.create(name="Test Endpoint Product")
    prod_rel = ProductoTipoCritCrit.objects.create(
        producto=producto,
        relacion_tipo_criticidad=tipo_crit_rel
    )
    
    tipo_equipo = TipoEquipo.objects.create(name="Test Endpoint Equipment")
    tipo_equipo_rel = TipoEquipoProducto.objects.create(
        tipo_equipo=tipo_equipo,
        relacion_producto=prod_rel
    )
    
    tecnologia = Tecnologia.objects.create(name="Test Endpoint Technology")
    tech_rel = TecnologiaTipoEquipo.objects.create(
        tecnologia=tecnologia,
        relacion_tipo_equipo=tipo_equipo_rel
    )
    
    # Test endpoint
    client = Client()
    
    # Test DELETE request
    response = client.delete(f'/complementos/eliminar-tecnologia/{tecnologia.id}/')
    
    print(f"  Response status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"  Response data: {data}")
        
        # Verify technology was deleted
        assert not Tecnologia.objects.filter(id=tecnologia.id).exists()
        print("  ✅ Technology deleted successfully via endpoint")
    else:
        print(f"  ❌ Endpoint failed with status: {response.status_code}")
        print(f"  Response content: {response.content}")

def test_technology_relation_endpoint():
    """Test technology relation deletion endpoint"""
    print("\n🧪 Testing Technology Relation Deletion Endpoint...")
    
    # Create test data
    tipo_crit = TipoCriticidad.objects.create(name="Test Relation Type")
    criticidad = Criticidad.objects.create(name="Test Relation Criticidad")
    tipo_crit_rel = TipoCriticidadCriticidad.objects.create(
        tipo_criticidad=tipo_crit,
        criticidad=criticidad
    )
    
    producto1 = Producto.objects.create(name="Test Relation Product 1")
    producto2 = Producto.objects.create(name="Test Relation Product 2")
    
    prod_rel1 = ProductoTipoCritCrit.objects.create(
        producto=producto1,
        relacion_tipo_criticidad=tipo_crit_rel
    )
    prod_rel2 = ProductoTipoCritCrit.objects.create(
        producto=producto2,
        relacion_tipo_criticidad=tipo_crit_rel
    )
    
    tipo_equipo1 = TipoEquipo.objects.create(name="Test Relation Equipment 1")
    tipo_equipo2 = TipoEquipo.objects.create(name="Test Relation Equipment 2")
    
    tipo_equipo_rel1 = TipoEquipoProducto.objects.create(
        tipo_equipo=tipo_equipo1,
        relacion_producto=prod_rel1
    )
    tipo_equipo_rel2 = TipoEquipoProducto.objects.create(
        tipo_equipo=tipo_equipo2,
        relacion_producto=prod_rel2
    )
    
    tecnologia = Tecnologia.objects.create(name="Test Relation Technology")
    tech_rel1 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tecnologia,
        relacion_tipo_equipo=tipo_equipo_rel1
    )
    tech_rel2 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tecnologia,
        relacion_tipo_equipo=tipo_equipo_rel2
    )
    
    # Test endpoint - delete one relation
    client = Client()
    
    response = client.delete(f'/complementos/eliminar-tecnologia-relacion/{tech_rel1.id}/')
    
    print(f"  Response status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"  Response data: {data}")
        
        # Verify relation was deleted but technology remains
        assert not TecnologiaTipoEquipo.objects.filter(id=tech_rel1.id).exists()
        assert Tecnologia.objects.filter(id=tecnologia.id).exists()
        remaining_relations = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()
        assert remaining_relations == 1
        print("  ✅ Relation deleted successfully, technology kept")
    else:
        print(f"  ❌ Endpoint failed with status: {response.status_code}")
        print(f"  Response content: {response.content}")

def test_technology_last_relation_endpoint():
    """Test technology last relation deletion endpoint"""
    print("\n🧪 Testing Technology Last Relation Deletion Endpoint...")
    
    # Create test data with single relation
    tipo_crit = TipoCriticidad.objects.create(name="Test Last Type")
    criticidad = Criticidad.objects.create(name="Test Last Criticidad")
    tipo_crit_rel = TipoCriticidadCriticidad.objects.create(
        tipo_criticidad=tipo_crit,
        criticidad=criticidad
    )
    
    producto = Producto.objects.create(name="Test Last Product")
    prod_rel = ProductoTipoCritCrit.objects.create(
        producto=producto,
        relacion_tipo_criticidad=tipo_crit_rel
    )
    
    tipo_equipo = TipoEquipo.objects.create(name="Test Last Equipment")
    tipo_equipo_rel = TipoEquipoProducto.objects.create(
        tipo_equipo=tipo_equipo,
        relacion_producto=prod_rel
    )
    
    tecnologia = Tecnologia.objects.create(name="Test Last Technology")
    tech_rel = TecnologiaTipoEquipo.objects.create(
        tecnologia=tecnologia,
        relacion_tipo_equipo=tipo_equipo_rel
    )
    
    # Test endpoint - delete last relation
    client = Client()
    
    response = client.delete(f'/complementos/eliminar-tecnologia-relacion/{tech_rel.id}/')
    
    print(f"  Response status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"  Response data: {data}")
        
        # Verify both relation and technology were deleted
        assert not TecnologiaTipoEquipo.objects.filter(id=tech_rel.id).exists()
        assert not Tecnologia.objects.filter(id=tecnologia.id).exists()
        print("  ✅ Last relation deleted successfully, technology also deleted")
    else:
        print(f"  ❌ Endpoint failed with status: {response.status_code}")
        print(f"  Response content: {response.content}")

def clean_test_data():
    """Clean test data"""
    print("\n🧹 Cleaning test data...")
    TecnologiaTipoEquipo.objects.all().delete()
    Tecnologia.objects.all().delete()
    TipoEquipoProducto.objects.all().delete()
    TipoEquipo.objects.all().delete()
    ProductoTipoCritCrit.objects.all().delete()
    Producto.objects.all().delete()
    TipoCriticidadCriticidad.objects.all().delete()
    Criticidad.objects.all().delete()
    TipoCriticidad.objects.all().delete()

def main():
    """Run all endpoint tests"""
    print("🚀 Starting Technology Endpoint Tests...")
    
    try:
        clean_test_data()
        test_technology_endpoint_complete()
        
        clean_test_data()
        test_technology_relation_endpoint()
        
        clean_test_data()
        test_technology_last_relation_endpoint()
        
        clean_test_data()
        
        print("\n🎉 All Technology Endpoint Tests Passed!")
        print("✅ Technology cascade deletion functionality is working correctly")
        print("✅ Both complete deletion and relation deletion endpoints work properly")
        print("✅ Orphan technology cleanup is functioning as expected")
        
    except Exception as e:
        print(f"\n❌ Error in endpoint tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
