#!/usr/bin/env python
"""
Test para verificar la lógica de actualización de Tecnología

Este script prueba que:
1. Al editar una Tecnología y cambiar su nombre a uno que no existe, actualiza el registro existente
2. Al editar una Tecnología y cambiar su nombre a uno que ya existe, usa el registro existente
3. Al editar sin cambiar el nombre, mantiene el mismo registro
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

def test_tecnologia_update_logic():
    print("🧪 Iniciando test de lógica de actualización de Tecnología...\n")
    
    # Limpiar datos existentes para el test
    print("🧹 Limpiando datos existentes...")
    TecnologiaTipoEquipo.objects.all().delete()
    Tecnologia.objects.all().delete()
    TipoCriticidadCriticidad.objects.all().delete()
    Criticidad.objects.all().delete()
    TipoCriticidad.objects.all().delete()
    ProductoTipoCritCrit.objects.all().delete()
    Producto.objects.all().delete()
    TipoEquipoProducto.objects.all().delete()
    TipoEquipo.objects.all().delete()
    
    # Crear datos de prueba
    print("📦 Creando datos de prueba...")
    
    # Crear TipoEquipo
    tipo_equipo = TipoEquipo.objects.create(name="Equipo Test")
    
    # Crear Producto
    producto = Producto.objects.create(name="Producto Test")
    
    # Crear TipoCriticidad
    tipo_criticidad = TipoCriticidad.objects.create(name="Tipo Criticidad Test")
    
    # Crear Criticidad
    criticidad = Criticidad.objects.create(name="Criticidad Test")
    
    # Crear relaciones
    relacion_criticidad = TipoCriticidadCriticidad.objects.create(
        tipo_criticidad=tipo_criticidad,
        criticidad=criticidad
    )
    
    relacion_producto = ProductoTipoCritCrit.objects.create(
        producto=producto,
        relacion_tipo_criticidad=relacion_criticidad
    )
    
    relacion_tipo_equipo = TipoEquipoProducto.objects.create(
        tipo_equipo=tipo_equipo,
        relacion_producto=relacion_producto
    )
    
    # Crear Tecnología inicial
    tecnologia_inicial = Tecnologia.objects.create(name="Tecnología Inicial")
    
    # Crear relación TecnologiaTipoEquipo
    relacion_tecnologia = TecnologiaTipoEquipo.objects.create(
        tecnologia=tecnologia_inicial,
        relacion_tipo_equipo=relacion_tipo_equipo
    )
    
    print(f"✅ Datos creados:")
    print(f"   - Tecnología inicial: '{tecnologia_inicial.name}' (ID: {tecnologia_inicial.id})")
    print(f"   - Relación TecnologiaTipoEquipo: ID {relacion_tecnologia.id}")
    
    # Verificar estado inicial
    tecnologias_antes = Tecnologia.objects.count()
    print(f"   - Total de Tecnologías antes: {tecnologias_antes}")
    
    # Test 1: Cambiar nombre a uno que no existe (debería actualizar registro existente)
    print("\n🔄 Test 1: Cambiar nombre a uno que no existe...")
    
    client = Client()
    update_data = {
        'name': 'Tecnología Actualizada',
        'tipo_equipo_id': tipo_equipo.id,
        'producto_id': producto.id,
        'tipo_criticidad_id': tipo_criticidad.id,
        'criticidad_id': criticidad.id
    }
    
    response = client.put(
        f'/complementos/tecnologia/editar/{relacion_tecnologia.id}/',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    print(f"   - Respuesta: {response.status_code}")
    
    # Verificar que no se creó una nueva Tecnología
    tecnologias_despues = Tecnologia.objects.count()
    print(f"   - Total de Tecnologías después: {tecnologias_despues}")
    
    # Verificar que se actualizó el nombre
    tecnologia_actualizada = Tecnologia.objects.get(id=tecnologia_inicial.id)
    print(f"   - Nombre actualizado: '{tecnologia_actualizada.name}'")
    
    assert tecnologias_antes == tecnologias_despues, "❌ ERROR: Se creó una nueva Tecnología en lugar de actualizar"
    assert tecnologia_actualizada.name == 'Tecnología Actualizada', "❌ ERROR: No se actualizó el nombre"
    print("   ✅ Test 1 PASÓ: Se actualizó el registro existente")
    
    # Test 2: Crear otra Tecnología y luego cambiar a un nombre que ya existe
    print("\n🔄 Test 2: Cambiar nombre a uno que ya existe...")
    
    # Crear otra Tecnología
    otra_tecnologia = Tecnologia.objects.create(name="Otra Tecnología")
    otra_relacion = TecnologiaTipoEquipo.objects.create(
        tecnologia=otra_tecnologia,
        relacion_tipo_equipo=relacion_tipo_equipo
    )
    
    tecnologias_antes_test2 = Tecnologia.objects.count()
    print(f"   - Total de Tecnologías antes: {tecnologias_antes_test2}")
    
    # Intentar cambiar a un nombre que ya existe
    update_data2 = {
        'name': 'Tecnología Actualizada',  # Este nombre ya existe
        'tipo_equipo_id': tipo_equipo.id,
        'producto_id': producto.id,
        'tipo_criticidad_id': tipo_criticidad.id,
        'criticidad_id': criticidad.id
    }
    
    response2 = client.put(
        f'/complementos/tecnologia/editar/{otra_relacion.id}/',
        data=json.dumps(update_data2),
        content_type='application/json'
    )
    
    print(f"   - Respuesta: {response2.status_code}")
    
    # Verificar que no se creó una nueva Tecnología
    tecnologias_despues_test2 = Tecnologia.objects.count()
    print(f"   - Total de Tecnologías después: {tecnologias_despues_test2}")
    
    # Verificar que la relación ahora apunta a la Tecnología existente
    otra_relacion.refresh_from_db()
    print(f"   - Tecnología de la relación: '{otra_relacion.tecnologia.name}' (ID: {otra_relacion.tecnologia.id})")
    
    assert tecnologias_antes_test2 == tecnologias_despues_test2, "❌ ERROR: Se creó una nueva Tecnología"
    assert otra_relacion.tecnologia.id == tecnologia_actualizada.id, "❌ ERROR: No se usó la Tecnología existente"
    print("   ✅ Test 2 PASÓ: Se usó la Tecnología existente")
    
    # Test 3: Cambiar sin modificar el nombre
    print("\n🔄 Test 3: Actualizar sin cambiar el nombre...")
    
    tecnologias_antes_test3 = Tecnologia.objects.count()
    tecnologia_id_antes = otra_relacion.tecnologia.id
    
    update_data3 = {
        'name': 'Tecnología Actualizada',  # Mismo nombre
        'tipo_equipo_id': tipo_equipo.id,
        'producto_id': producto.id,
        'tipo_criticidad_id': tipo_criticidad.id,
        'criticidad_id': criticidad.id
    }
    
    response3 = client.put(
        f'/complementos/tecnologia/editar/{otra_relacion.id}/',
        data=json.dumps(update_data3),
        content_type='application/json'
    )
    
    tecnologias_despues_test3 = Tecnologia.objects.count()
    otra_relacion.refresh_from_db()
    
    assert tecnologias_antes_test3 == tecnologias_despues_test3, "❌ ERROR: Se modificó el número de Tecnologías"
    assert otra_relacion.tecnologia.id == tecnologia_id_antes, "❌ ERROR: Se cambió la Tecnología"
    print("   ✅ Test 3 PASÓ: Se mantuvo la misma Tecnología")
    
    print("\n🎉 ¡Todos los tests pasaron! La lógica de actualización funciona correctamente.")
    
    # Limpiar datos de prueba
    print("\n🧹 Limpiando datos de prueba...")
    TecnologiaTipoEquipo.objects.all().delete()
    Tecnologia.objects.all().delete()
    TipoCriticidadCriticidad.objects.all().delete()
    Criticidad.objects.all().delete()
    TipoCriticidad.objects.all().delete()
    ProductoTipoCritCrit.objects.all().delete()
    Producto.objects.all().delete()
    TipoEquipoProducto.objects.all().delete()
    TipoEquipo.objects.all().delete()
    
    print("✅ Test completado exitosamente!")

if __name__ == "__main__":
    test_tecnologia_update_logic()
