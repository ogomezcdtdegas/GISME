#!/usr/bin/env python3
"""
Script para probar la eliminación completa de criticidad con toda la cadena de dependencias.
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

def crear_datos_prueba():
    """Crear datos de prueba para la eliminación completa."""
    print("🔄 Creando datos de prueba para eliminación completa...")
    
    with transaction.atomic():
        # 1. Crear criticidad de prueba
        criticidad_test = Criticidad.objects.create(name="Criticidad Test Eliminación")
        print(f"✅ Criticidad creada: {criticidad_test.name}")
        
        # 2. Crear tipo de criticidad
        tipo_criticidad_test = TipoCriticidad.objects.create(name="Tipo Test Eliminación")
        print(f"✅ Tipo de criticidad creado: {tipo_criticidad_test.name}")
        
        # 3. Crear relación tipo-criticidad
        relacion_tipo_crit = TipoCriticidadCriticidad.objects.create(
            tipo_criticidad=tipo_criticidad_test,
            criticidad=criticidad_test
        )
        print(f"✅ Relación tipo-criticidad creada: {relacion_tipo_crit}")
        
        # 4. Crear producto
        producto_test = Producto.objects.create(name="Producto Test Eliminación")
        print(f"✅ Producto creado: {producto_test.name}")
        
        # 5. Crear relación producto-tipo-criticidad
        relacion_producto = ProductoTipoCritCrit.objects.create(
            producto=producto_test,
            relacion_tipo_criticidad=relacion_tipo_crit
        )
        print(f"✅ Relación producto-tipo-criticidad creada: {relacion_producto}")
        
        # 6. Crear tipo de equipo
        tipo_equipo_test = TipoEquipo.objects.create(name="Tipo Equipo Test Eliminación")
        print(f"✅ Tipo de equipo creado: {tipo_equipo_test.name}")
        
        # 7. Crear relación tipo equipo-producto
        relacion_tipo_equipo = TipoEquipoProducto.objects.create(
            tipo_equipo=tipo_equipo_test,
            relacion_producto=relacion_producto
        )
        print(f"✅ Relación tipo equipo-producto creada: {relacion_tipo_equipo}")
        
        # 8. Crear tecnología
        tecnologia_test = Tecnologia.objects.create(name="Tecnología Test Eliminación")
        print(f"✅ Tecnología creada: {tecnologia_test.name}")
        
        # 9. Crear relación tecnología-tipo equipo
        relacion_tecnologia = TecnologiaTipoEquipo.objects.create(
            tecnologia=tecnologia_test,
            relacion_tipo_equipo=relacion_tipo_equipo
        )
        print(f"✅ Relación tecnología-tipo equipo creada: {relacion_tecnologia}")
        
        print(f"\n🎯 Cadena completa creada:")
        print(f"   Criticidad: {criticidad_test.name}")
        print(f"   → Tipo: {tipo_criticidad_test.name}")
        print(f"   → Producto: {producto_test.name}")
        print(f"   → Tipo Equipo: {tipo_equipo_test.name}")
        print(f"   → Tecnología: {tecnologia_test.name}")
        
        return criticidad_test.id

def verificar_datos_antes():
    """Verificar que existen los datos antes de la eliminación."""
    print("\n📊 Verificando datos antes de la eliminación:")
    
    criticidades = Criticidad.objects.filter(name__contains="Test Eliminación")
    tipos = TipoCriticidad.objects.filter(name__contains="Test Eliminación")
    productos = Producto.objects.filter(name__contains="Test Eliminación")
    tipos_equipo = TipoEquipo.objects.filter(name__contains="Test Eliminación")
    tecnologias = Tecnologia.objects.filter(name__contains="Test Eliminación")
    
    print(f"   Criticidades: {criticidades.count()}")
    print(f"   Tipos de criticidad: {tipos.count()}")
    print(f"   Productos: {productos.count()}")
    print(f"   Tipos de equipo: {tipos_equipo.count()}")
    print(f"   Tecnologías: {tecnologias.count()}")
    
    # Verificar relaciones
    relaciones_tipo_crit = TipoCriticidadCriticidad.objects.filter(
        criticidad__name__contains="Test Eliminación"
    )
    relaciones_producto = ProductoTipoCritCrit.objects.filter(
        producto__name__contains="Test Eliminación"
    )
    relaciones_tipo_equipo = TipoEquipoProducto.objects.filter(
        tipo_equipo__name__contains="Test Eliminación"
    )
    relaciones_tecnologia = TecnologiaTipoEquipo.objects.filter(
        tecnologia__name__contains="Test Eliminación"
    )
    
    print(f"\n   Relaciones tipo-criticidad: {relaciones_tipo_crit.count()}")
    print(f"   Relaciones producto-tipo-criticidad: {relaciones_producto.count()}")
    print(f"   Relaciones tipo equipo-producto: {relaciones_tipo_equipo.count()}")
    print(f"   Relaciones tecnología-tipo equipo: {relaciones_tecnologia.count()}")

def verificar_datos_despues():
    """Verificar que se eliminaron todos los datos después de la eliminación."""
    print("\n📊 Verificando datos después de la eliminación:")
    
    criticidades = Criticidad.objects.filter(name__contains="Test Eliminación")
    tipos = TipoCriticidad.objects.filter(name__contains="Test Eliminación")
    productos = Producto.objects.filter(name__contains="Test Eliminación")
    tipos_equipo = TipoEquipo.objects.filter(name__contains="Test Eliminación")
    tecnologias = Tecnologia.objects.filter(name__contains="Test Eliminación")
    
    print(f"   Criticidades: {criticidades.count()}")
    print(f"   Tipos de criticidad: {tipos.count()}")
    print(f"   Productos: {productos.count()}")
    print(f"   Tipos de equipo: {tipos_equipo.count()}")
    print(f"   Tecnologías: {tecnologias.count()}")
    
    # Verificar relaciones
    relaciones_tipo_crit = TipoCriticidadCriticidad.objects.filter(
        criticidad__name__contains="Test Eliminación"
    )
    relaciones_producto = ProductoTipoCritCrit.objects.filter(
        producto__name__contains="Test Eliminación"
    )
    relaciones_tipo_equipo = TipoEquipoProducto.objects.filter(
        tipo_equipo__name__contains="Test Eliminación"
    )
    relaciones_tecnologia = TecnologiaTipoEquipo.objects.filter(
        tecnologia__name__contains="Test Eliminación"
    )
    
    print(f"\n   Relaciones tipo-criticidad: {relaciones_tipo_crit.count()}")
    print(f"   Relaciones producto-tipo-criticidad: {relaciones_producto.count()}")
    print(f"   Relaciones tipo equipo-producto: {relaciones_tipo_equipo.count()}")
    print(f"   Relaciones tecnología-tipo equipo: {relaciones_tecnologia.count()}")
    
    # Verificar que todo está en 0
    total_elementos = (
        criticidades.count() + tipos.count() + productos.count() + 
        tipos_equipo.count() + tecnologias.count()
    )
    total_relaciones = (
        relaciones_tipo_crit.count() + relaciones_producto.count() + 
        relaciones_tipo_equipo.count() + relaciones_tecnologia.count()
    )
    
    if total_elementos == 0 and total_relaciones == 0:
        print("\n✅ ÉXITO: Todos los elementos y relaciones fueron eliminados correctamente")
    else:
        print(f"\n❌ ERROR: Aún quedan {total_elementos} elementos y {total_relaciones} relaciones")

def main():
    print("🚀 Iniciando prueba de eliminación completa de criticidad")
    
    try:
        # 1. Crear datos de prueba
        criticidad_id = crear_datos_prueba()
        
        # 2. Verificar datos antes
        verificar_datos_antes()
        
        # 3. Simular la eliminación usando el comando
        print(f"\n🗑️  Eliminando criticidad con ID: {criticidad_id}")
        
        # Importar y ejecutar el comando
        from _AppComplementos.views.views_Criticidad.Commands.DeleteCriticidadCommand.DeleteCriticidadCommand import DeleteCriticidadCommand
        from django.http import HttpRequest
        
        # Simular request
        request = HttpRequest()
        request.method = 'DELETE'
        
        # Ejecutar el comando
        command = DeleteCriticidadCommand()
        response = command.delete(request, criticidad_id)
        
        print(f"✅ Comando ejecutado. Status: {response.status_code}")
        print(f"📄 Respuesta: {response.data}")
        
        # 4. Verificar datos después
        verificar_datos_despues()
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
