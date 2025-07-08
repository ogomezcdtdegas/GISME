#!/usr/bin/env python3
"""
Script para probar la eliminación parcial de criticidad - algunos elementos deben conservarse.
"""

import os
import sys
import django

# Configurar Django
sys.path.append('d:/EQ-456/Escritorio/GISME')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import (
    Criticidad, TipoCriticidad, Producto, TipoCriticidadCriticidad,
    ProductoTipoCritCrit, TipoEquipo, TipoEquipoProducto, 
    Tecnologia, TecnologiaTipoEquipo
)
from django.db import transaction

def crear_datos_prueba_compleja():
    """Crear datos de prueba más complejos donde algunos elementos deben conservarse."""
    print("🔄 Creando datos de prueba complejos...")
    
    with transaction.atomic():
        # Crear criticidades
        criticidad_eliminar = Criticidad.objects.create(name="Criticidad A Eliminar")
        criticidad_conservar = Criticidad.objects.create(name="Criticidad A Conservar")
        
        # Crear tipos de criticidad
        tipo_solo_eliminar = TipoCriticidad.objects.create(name="Tipo Solo Eliminar")
        tipo_compartido = TipoCriticidad.objects.create(name="Tipo Compartido")
        
        # Crear productos
        producto_solo_eliminar = Producto.objects.create(name="Producto Solo Eliminar")
        producto_compartido = Producto.objects.create(name="Producto Compartido")
        
        # Crear tipos de equipo
        tipo_equipo_solo_eliminar = TipoEquipo.objects.create(name="TipoEquipo Solo Eliminar")
        tipo_equipo_compartido = TipoEquipo.objects.create(name="TipoEquipo Compartido")
        
        # Crear tecnologías
        tecnologia_solo_eliminar = Tecnologia.objects.create(name="Tecnologia Solo Eliminar")
        tecnologia_compartida = Tecnologia.objects.create(name="Tecnologia Compartida")
        
        # CADENA 1: Solo con criticidad a eliminar (se debe eliminar completamente)
        rel_tipo_crit_1 = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_solo_eliminar,
            criticidad=criticidad_eliminar
        )
        rel_producto_1 = ProductoTipoCritCrit.objects.create(
            producto=producto_solo_eliminar,
            relacion_tipo_criticidad=rel_tipo_crit_1
        )
        rel_tipo_equipo_1 = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_equipo_solo_eliminar,
            relacion_producto=rel_producto_1
        )
        rel_tecnologia_1 = TecnologiaTipoEquipo.objects.create(
            tecnologia=tecnologia_solo_eliminar,
            relacion_tipo_equipo=rel_tipo_equipo_1
        )
        
        # CADENA 2: Elementos compartidos (se deben conservar)
        rel_tipo_crit_2a = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_compartido,
            criticidad=criticidad_eliminar  # Está con la criticidad a eliminar
        )
        rel_tipo_crit_2b = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_compartido,
            criticidad=criticidad_conservar  # Pero también con otra criticidad
        )
        
        # Producto compartido con ambas criticidades
        rel_producto_2a = ProductoTipoCritCrit.objects.create(
            producto=producto_compartido,
            relacion_tipo_criticidad=rel_tipo_crit_2a
        )
        rel_producto_2b = ProductoTipoCritCrit.objects.create(
            producto=producto_compartido,
            relacion_tipo_criticidad=rel_tipo_crit_2b
        )
        
        # Tipo equipo compartido con ambos productos
        rel_tipo_equipo_2a = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_equipo_compartido,
            relacion_producto=rel_producto_2a
        )
        rel_tipo_equipo_2b = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_equipo_compartido,
            relacion_producto=rel_producto_2b
        )
        
        # Tecnología compartida con ambos tipos de equipo
        rel_tecnologia_2a = TecnologiaTipoEquipo.objects.create(
            tecnologia=tecnologia_compartida,
            relacion_tipo_equipo=rel_tipo_equipo_2a
        )
        rel_tecnologia_2b = TecnologiaTipoEquipo.objects.create(
            tecnologia=tecnologia_compartida,
            relacion_tipo_equipo=rel_tipo_equipo_2b
        )
        
        print("✅ Datos complejos creados:")
        print(f"   Criticidad a eliminar: {criticidad_eliminar.name}")
        print(f"   Criticidad a conservar: {criticidad_conservar.name}")
        print(f"   Tipo solo eliminar: {tipo_solo_eliminar.name}")
        print(f"   Tipo compartido: {tipo_compartido.name}")
        print(f"   Producto solo eliminar: {producto_solo_eliminar.name}")
        print(f"   Producto compartido: {producto_compartido.name}")
        
        return criticidad_eliminar.id

def verificar_datos_antes():
    """Verificar datos antes de la eliminación."""
    print("\n📊 Verificando datos antes de la eliminación:")
    
    # Contar elementos
    print(f"   Criticidades: {Criticidad.objects.count()}")
    print(f"   Tipos de criticidad: {TipoCriticidad.objects.count()}")
    print(f"   Productos: {Producto.objects.count()}")
    print(f"   Tipos de equipo: {TipoEquipo.objects.count()}")
    print(f"   Tecnologías: {Tecnologia.objects.count()}")
    
    # Contar relaciones
    print(f"   Relaciones tipo-criticidad: {TipoCriticidadCriticidad.objects.count()}")
    print(f"   Relaciones producto-tipo-criticidad: {ProductoTipoCritCrit.objects.count()}")
    print(f"   Relaciones tipo equipo-producto: {TipoEquipoProducto.objects.count()}")
    print(f"   Relaciones tecnología-tipo equipo: {TecnologiaTipoEquipo.objects.count()}")

def verificar_datos_despues():
    """Verificar datos después de la eliminación."""
    print("\n📊 Verificando datos después de la eliminación:")
    
    # Elementos que deben haberse eliminado
    eliminados = {
        'Criticidad A Eliminar': Criticidad.objects.filter(name="Criticidad A Eliminar").count(),
        'Tipo Solo Eliminar': TipoCriticidad.objects.filter(name="Tipo Solo Eliminar").count(),
        'Producto Solo Eliminar': Producto.objects.filter(name="Producto Solo Eliminar").count(),
        'TipoEquipo Solo Eliminar': TipoEquipo.objects.filter(name="TipoEquipo Solo Eliminar").count(),
        'Tecnologia Solo Eliminar': Tecnologia.objects.filter(name="Tecnologia Solo Eliminar").count(),
    }
    
    # Elementos que deben haberse conservado
    conservados = {
        'Criticidad A Conservar': Criticidad.objects.filter(name="Criticidad A Conservar").count(),
        'Tipo Compartido': TipoCriticidad.objects.filter(name="Tipo Compartido").count(),
        'Producto Compartido': Producto.objects.filter(name="Producto Compartido").count(),
        'TipoEquipo Compartido': TipoEquipo.objects.filter(name="TipoEquipo Compartido").count(),
        'Tecnologia Compartida': Tecnologia.objects.filter(name="Tecnologia Compartida").count(),
    }
    
    print("\n   🗑️  Elementos que debían eliminarse:")
    errores_eliminacion = 0
    for nombre, count in eliminados.items():
        if count == 0:
            print(f"      ✅ {nombre}: eliminado correctamente")
        else:
            print(f"      ❌ {nombre}: ERROR - no se eliminó ({count} encontrado)")
            errores_eliminacion += 1
    
    print("\n   💾 Elementos que debían conservarse:")
    errores_conservacion = 0
    for nombre, count in conservados.items():
        if count == 1:
            print(f"      ✅ {nombre}: conservado correctamente")
        else:
            print(f"      ❌ {nombre}: ERROR - no se conservó ({count} encontrado)")
            errores_conservacion += 1
    
    # Verificar relaciones conservadas
    rel_conservadas = TipoCriticidadCriticidad.objects.filter(
        criticidad__name="Criticidad A Conservar"
    ).count()
    
    print(f"\n   Relaciones conservadas con 'Criticidad A Conservar': {rel_conservadas}")
    
    if errores_eliminacion == 0 and errores_conservacion == 0:
        print("\n✅ ÉXITO: Eliminación selectiva funcionó correctamente")
    else:
        print(f"\n❌ ERROR: {errores_eliminacion} errores de eliminación, {errores_conservacion} errores de conservación")

def main():
    print("🚀 Iniciando prueba de eliminación parcial de criticidad")
    
    try:
        # 1. Crear datos de prueba complejos
        criticidad_id = crear_datos_prueba_compleja()
        
        # 2. Verificar datos antes
        verificar_datos_antes()
        
        # 3. Ejecutar la eliminación
        print(f"\n🗑️  Eliminando criticidad 'Criticidad A Eliminar' con ID: {criticidad_id}")
        
        from _AppComplementos.views.views_Criticidad.Commands.DeleteCriticidadCommand.DeleteCriticidadCommand import DeleteCriticidadCommand
        from django.http import HttpRequest
        
        request = HttpRequest()
        request.method = 'DELETE'
        
        command = DeleteCriticidadCommand()
        response = command.delete(request, criticidad_id)
        
        print(f"✅ Comando ejecutado. Status: {response.status_code}")
        print(f"📄 Respuesta: {response.data}")
        
        # 4. Verificar resultados
        verificar_datos_despues()
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
