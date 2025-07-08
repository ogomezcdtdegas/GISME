#!/usr/bin/env python
"""
Test para verificar la eliminación en cascada de Tecnología

Este script prueba que:
1. Al eliminar una Tecnología, se eliminen todas sus relaciones
2. Al eliminar una relación específica, se mantenga la Tecnología si tiene otras relaciones
3. Al eliminar la última relación de una Tecnología, se elimine la Tecnología completa
4. La eliminación en cascada funciona correctamente desde el nivel superior
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import *

def limpiar_datos():
    """Limpia todos los datos para empezar fresh"""
    print("🧹 Limpiando datos existentes...")
    TecnologiaTipoEquipo.objects.all().delete()
    Tecnologia.objects.all().delete()
    TipoEquipoProducto.objects.all().delete()
    TipoEquipo.objects.all().delete()
    ProductoTipoCritCrit.objects.all().delete()
    Producto.objects.all().delete()
    TipoCriticidadCriticidad.objects.all().delete()
    Criticidad.objects.all().delete()
    TipoCriticidad.objects.all().delete()

def crear_datos_prueba():
    """Crea datos de prueba para el test"""
    print("📦 Creando datos de prueba...")
    
    # Crear TipoCriticidad
    tipo_crit = TipoCriticidad.objects.create(name="TipoCrit Test")
    
    # Crear Criticidad
    criticidad = Criticidad.objects.create(name="Criticidad Test")
    
    # Crear relación TipoCriticidad-Criticidad
    tipo_crit_rel = TipoCriticidadCriticidad.objects.create(
        tipoCriticidad=tipo_crit,
        criticidad=criticidad
    )
    
    # Crear Productos
    producto1 = Producto.objects.create(name="Producto Test 1")
    producto2 = Producto.objects.create(name="Producto Test 2")
    
    # Crear relaciones Producto-TipoCriticidad-Criticidad
    prod_rel1 = ProductoTipoCritCrit.objects.create(
        producto=producto1,
        tipoCriticidadCriticidad=tipo_crit_rel
    )
    prod_rel2 = ProductoTipoCritCrit.objects.create(
        producto=producto2,
        tipoCriticidadCriticidad=tipo_crit_rel
    )
    
    # Crear TipoEquipos
    tipo_equipo1 = TipoEquipo.objects.create(name="TipoEquipo Test 1")
    tipo_equipo2 = TipoEquipo.objects.create(name="TipoEquipo Test 2")
    
    # Crear relaciones TipoEquipo-Producto
    tipo_equipo_rel1 = TipoEquipoProducto.objects.create(
        tipoEquipo=tipo_equipo1,
        productoTipoCritCrit=prod_rel1
    )
    tipo_equipo_rel2 = TipoEquipoProducto.objects.create(
        tipoEquipo=tipo_equipo2,
        productoTipoCritCrit=prod_rel2
    )
    
    # Crear Tecnologías
    tecnologia1 = Tecnologia.objects.create(name="Tecnología Test 1")
    tecnologia2 = Tecnologia.objects.create(name="Tecnología Test 2")
    tecnologia3 = Tecnologia.objects.create(name="Tecnología Compartida")
    
    # Crear relaciones Tecnología-TipoEquipo
    tech_rel1 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tecnologia1,
        tipoEquipoProducto=tipo_equipo_rel1
    )
    tech_rel2 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tecnologia2,
        tipoEquipoProducto=tipo_equipo_rel2
    )
    # Tecnología compartida con múltiples relaciones
    tech_rel3 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tecnologia3,
        tipoEquipoProducto=tipo_equipo_rel1
    )
    tech_rel4 = TecnologiaTipoEquipo.objects.create(
        tecnologia=tecnologia3,
        tipoEquipoProducto=tipo_equipo_rel2
    )
    
    return {
        'tecnologia1': tecnologia1,
        'tecnologia2': tecnologia2,
        'tecnologia_compartida': tecnologia3,
        'tech_rel1': tech_rel1,
        'tech_rel2': tech_rel2,
        'tech_rel3': tech_rel3,
        'tech_rel4': tech_rel4,
        'tipo_equipo1': tipo_equipo1,
        'tipo_equipo2': tipo_equipo2,
    }

def test_eliminacion_tecnologia_completa():
    """Test: Eliminar una Tecnología completa"""
    print("\n🧪 Test 1: Eliminación completa de Tecnología")
    
    datos = crear_datos_prueba()
    
    # Verificar estado inicial
    print(f"   Estado inicial:")
    print(f"   - Tecnologías: {Tecnologia.objects.count()}")
    print(f"   - Relaciones Tecnología-TipoEquipo: {TecnologiaTipoEquipo.objects.count()}")
    
    # Eliminar tecnología1 (tiene 1 relación)
    tecnologia_id = datos['tecnologia1'].id
    print(f"   Eliminando Tecnología '{datos['tecnologia1'].name}' (ID: {tecnologia_id})")
    
    # Simular el comando de eliminación
    from _AppComplementos.views.views_Tecnologia.Commands.DeleteTecnologiaCommand.DeleteTecnologiaCommand import DeleteTecnologiaCommand
    
    command = DeleteTecnologiaCommand()
    result = command.execute(tecnologia_id)
    
    print(f"   Resultado: {result}")
    
    # Verificar estado final
    print(f"   Estado final:")
    print(f"   - Tecnologías: {Tecnologia.objects.count()}")
    print(f"   - Relaciones Tecnología-TipoEquipo: {TecnologiaTipoEquipo.objects.count()}")
    
    # Verificar que la tecnología fue eliminada
    assert not Tecnologia.objects.filter(id=tecnologia_id).exists(), "La tecnología no fue eliminada"
    print("   ✅ Tecnología eliminada correctamente")
    
    limpiar_datos()

def test_eliminacion_relacion_tecnologia():
    """Test: Eliminar una relación específica de Tecnología"""
    print("\n🧪 Test 2: Eliminación de relación específica de Tecnología")
    
    datos = crear_datos_prueba()
    
    # Verificar estado inicial
    tecnologia_compartida = datos['tecnologia_compartida']
    relaciones_iniciales = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia_compartida).count()
    print(f"   Estado inicial:")
    print(f"   - Tecnología '{tecnologia_compartida.name}' tiene {relaciones_iniciales} relaciones")
    
    # Eliminar una relación específica
    relacion_id = datos['tech_rel3'].id
    print(f"   Eliminando relación específica (ID: {relacion_id})")
    
    # Simular el comando de eliminación de relación
    from _AppComplementos.views.views_Tecnologia.Commands.DeleteTecnologiaRelacionCommand.DeleteTecnologiaRelacionCommand import DeleteTecnologiaRelacionCommand
    
    command = DeleteTecnologiaRelacionCommand()
    result = command.execute(relacion_id)
    
    print(f"   Resultado: {result}")
    
    # Verificar estado final
    relaciones_finales = TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia_compartida).count()
    print(f"   Estado final:")
    print(f"   - Tecnología '{tecnologia_compartida.name}' tiene {relaciones_finales} relaciones")
    
    # Verificar que la relación fue eliminada pero la tecnología permanece
    assert not TecnologiaTipoEquipo.objects.filter(id=relacion_id).exists(), "La relación no fue eliminada"
    assert Tecnologia.objects.filter(id=tecnologia_compartida.id).exists(), "La tecnología fue eliminada incorrectamente"
    assert relaciones_finales == relaciones_iniciales - 1, "El número de relaciones no es correcto"
    print("   ✅ Relación eliminada correctamente, tecnología mantenida")
    
    limpiar_datos()

def test_eliminacion_ultima_relacion():
    """Test: Eliminar la última relación de una Tecnología"""
    print("\n🧪 Test 3: Eliminación de última relación de Tecnología")
    
    datos = crear_datos_prueba()
    
    # Usar tecnología2 que tiene solo 1 relación
    tecnologia = datos['tecnologia2']
    relacion = datos['tech_rel2']
    
    print(f"   Estado inicial:")
    print(f"   - Tecnología '{tecnologia.name}' tiene {TecnologiaTipoEquipo.objects.filter(tecnologia=tecnologia).count()} relación(es)")
    
    # Eliminar la única relación
    relacion_id = relacion.id
    tecnologia_id = tecnologia.id
    print(f"   Eliminando última relación (ID: {relacion_id})")
    
    # Simular el comando de eliminación de relación
    from _AppComplementos.views.views_Tecnologia.Commands.DeleteTecnologiaRelacionCommand.DeleteTecnologiaRelacionCommand import DeleteTecnologiaRelacionCommand
    
    command = DeleteTecnologiaRelacionCommand()
    result = command.execute(relacion_id)
    
    print(f"   Resultado: {result}")
    
    # Verificar estado final
    print(f"   Estado final:")
    print(f"   - Tecnologías restantes: {Tecnologia.objects.count()}")
    print(f"   - Relaciones restantes: {TecnologiaTipoEquipo.objects.count()}")
    
    # Verificar que tanto la relación como la tecnología fueron eliminadas
    assert not TecnologiaTipoEquipo.objects.filter(id=relacion_id).exists(), "La relación no fue eliminada"
    assert not Tecnologia.objects.filter(id=tecnologia_id).exists(), "La tecnología no fue eliminada"
    print("   ✅ Última relación eliminada y tecnología eliminada correctamente")
    
    limpiar_datos()

def test_eliminacion_cascada_desde_tipo_equipo():
    """Test: Eliminación en cascada desde TipoEquipo afecta Tecnología"""
    print("\n🧪 Test 4: Eliminación en cascada desde TipoEquipo")
    
    datos = crear_datos_prueba()
    
    # Verificar estado inicial
    print(f"   Estado inicial:")
    print(f"   - TipoEquipos: {TipoEquipo.objects.count()}")
    print(f"   - Tecnologías: {Tecnologia.objects.count()}")
    print(f"   - Relaciones Tecnología-TipoEquipo: {TecnologiaTipoEquipo.objects.count()}")
    
    # Eliminar tipo_equipo1 (debería eliminar tecnologia1 y afectar tecnologia_compartida)
    tipo_equipo_id = datos['tipo_equipo1'].id
    print(f"   Eliminando TipoEquipo '{datos['tipo_equipo1'].name}' (ID: {tipo_equipo_id})")
    
    # Simular el comando de eliminación de TipoEquipo
    from _AppComplementos.views.views_TipoEquipo.Commands.DeleteTipoEquipoCommand.DeleteTipoEquipoCommand import DeleteTipoEquipoCommand
    
    command = DeleteTipoEquipoCommand()
    result = command.execute(tipo_equipo_id)
    
    print(f"   Resultado: {result}")
    
    # Verificar estado final
    print(f"   Estado final:")
    print(f"   - TipoEquipos: {TipoEquipo.objects.count()}")
    print(f"   - Tecnologías: {Tecnologia.objects.count()}")
    print(f"   - Relaciones Tecnología-TipoEquipo: {TecnologiaTipoEquipo.objects.count()}")
    
    # Verificar que la tecnología1 fue eliminada (solo tenía relación con tipo_equipo1)
    assert not Tecnologia.objects.filter(id=datos['tecnologia1'].id).exists(), "Tecnología1 no fue eliminada"
    # Verificar que la tecnología_compartida permanece (tiene relación con tipo_equipo2)
    assert Tecnologia.objects.filter(id=datos['tecnologia_compartida'].id).exists(), "Tecnología compartida fue eliminada incorrectamente"
    
    print("   ✅ Eliminación en cascada desde TipoEquipo funciona correctamente")
    
    limpiar_datos()

def run_all_tests():
    """Ejecuta todos los tests"""
    print("🚀 Iniciando tests de eliminación de Tecnología...\n")
    
    try:
        test_eliminacion_tecnologia_completa()
        test_eliminacion_relacion_tecnologia()
        test_eliminacion_ultima_relacion()
        test_eliminacion_cascada_desde_tipo_equipo()
        
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        print("✅ La funcionalidad de eliminación en cascada de Tecnología funciona correctamente")
        
    except Exception as e:
        print(f"\n❌ Error en los tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
