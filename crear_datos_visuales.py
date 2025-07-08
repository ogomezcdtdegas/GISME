#!/usr/bin/env python3
"""
Script para agregar datos de prueba visuales.
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

def crear_datos_visuales():
    """Crear datos para prueba visual."""
    print("🎨 Creando datos para prueba visual...")
    
    with transaction.atomic():
        # Crear criticidad que se puede eliminar para prueba
        try:
            criticidad_visual = Criticidad.objects.create(name="Criticidad Prueba Visual")
            tipo_visual = TipoCriticidad.objects.create(name="Tipo Prueba Visual")
            producto_visual = Producto.objects.create(name="Producto Prueba Visual")
            equipo_visual = TipoEquipo.objects.create(name="Equipo Prueba Visual")
            tech_visual = Tecnologia.objects.create(name="Tecnología Prueba Visual")
            
            # Crear relaciones
            rel_tipo = TipoCriticidadCriticidad.objects.create(
                tipo_criticidad=tipo_visual,
                criticidad=criticidad_visual
            )
            rel_producto = ProductoTipoCritCrit.objects.create(
                producto=producto_visual,
                relacion_tipo_criticidad=rel_tipo
            )
            rel_equipo = TipoEquipoProducto.objects.create(
                tipo_equipo=equipo_visual,
                relacion_producto=rel_producto
            )
            rel_tech = TecnologiaTipoEquipo.objects.create(
                tecnologia=tech_visual,
                relacion_tipo_equipo=rel_equipo
            )
            
            print("✅ Datos visuales creados exitosamente")
            print(f"   Criticidad: {criticidad_visual.name}")
            print(f"   → Tipo: {tipo_visual.name}")
            print(f"   → Producto: {producto_visual.name}")
            print(f"   → Equipo: {equipo_visual.name}")
            print(f"   → Tecnología: {tech_visual.name}")
            print("\n🎯 Ahora puedes probar la eliminación en el navegador!")
            
        except Exception as e:
            print(f"ℹ️  Los datos ya existen o hubo un error: {e}")

if __name__ == "__main__":
    crear_datos_visuales()
