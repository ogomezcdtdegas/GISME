"""
Script de prueba para verificar la eliminación en cascada de Tipo de Criticidad
"""

import os
import sys
import django

# Configurar Django
sys.path.append(r'd:\EQ-456\Escritorio\GISME')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import (
    Criticidad, TipoCriticidad, TipoCriticidadCriticidad,
    Producto, ProductoTipoCritCrit,
    TipoEquipo, TipoEquipoProducto,
    Tecnologia, TecnologiaTipoEquipo
)

def create_test_data():
    """Crear datos de prueba para la eliminación en cascada"""
    print("🔹 Creando datos de prueba para eliminación en cascada...")
    
    # Limpiar datos previos
    TecnologiaTipoEquipo.objects.filter(tecnologia__name__startswith="TechTest").delete()
    TipoEquipoProducto.objects.filter(tipo_equipo__name__startswith="EquipoTest").delete()
    ProductoTipoCritCrit.objects.filter(producto__name__startswith="ProdTest").delete()
    TipoCriticidadCriticidad.objects.filter(tipo_criticidad__name__startswith="TipoTest").delete()
    
    Tecnologia.objects.filter(name__startswith="TechTest").delete()
    TipoEquipo.objects.filter(name__startswith="EquipoTest").delete()
    Producto.objects.filter(name__startswith="ProdTest").delete()
    TipoCriticidad.objects.filter(name__startswith="TipoTest").delete()
    Criticidad.objects.filter(name__startswith="CritTest").delete()
    
    # Crear estructura completa
    
    # 1. Crear criticidades
    crit1 = Criticidad.objects.create(name="CritTest Alpha")
    crit2 = Criticidad.objects.create(name="CritTest Beta")
    
    # 2. Crear tipos de criticidad
    tipo1 = TipoCriticidad.objects.create(name="TipoTest Eliminable")  # Este será eliminado
    tipo2 = TipoCriticidad.objects.create(name="TipoTest Permanente")  # Este se mantendrá
    
    # 3. Crear relaciones tipo-criticidad
    rel1 = TipoCriticidadCriticidad.objects.create(tipo_criticidad=tipo1, criticidad=crit1)
    rel2 = TipoCriticidadCriticidad.objects.create(tipo_criticidad=tipo1, criticidad=crit2)
    rel3 = TipoCriticidadCriticidad.objects.create(tipo_criticidad=tipo2, criticidad=crit1)
    
    # 4. Crear productos
    prod1 = Producto.objects.create(name="ProdTest Solo")      # Solo tendrá tipo1 (será eliminado)
    prod2 = Producto.objects.create(name="ProdTest Compartido") # Tendrá tipo1 y tipo2 (se mantendrá)
    prod3 = Producto.objects.create(name="ProdTest Permanente") # Solo tendrá tipo2 (se mantendrá)
    
    # 5. Crear relaciones producto-tipo-criticidad
    prod_rel1 = ProductoTipoCritCrit.objects.create(producto=prod1, relacion_tipo_criticidad=rel1)
    prod_rel2 = ProductoTipoCritCrit.objects.create(producto=prod2, relacion_tipo_criticidad=rel1)
    prod_rel3 = ProductoTipoCritCrit.objects.create(producto=prod2, relacion_tipo_criticidad=rel3)
    prod_rel4 = ProductoTipoCritCrit.objects.create(producto=prod3, relacion_tipo_criticidad=rel3)
    
    # 6. Crear tipos de equipo
    equipo1 = TipoEquipo.objects.create(name="EquipoTest Solo")       # Solo tendrá prod1 (será eliminado)
    equipo2 = TipoEquipo.objects.create(name="EquipoTest Compartido") # Tendrá prod1 y prod2 (se mantendrá)
    equipo3 = TipoEquipo.objects.create(name="EquipoTest Permanente") # Solo tendrá prod3 (se mantendrá)
    
    # 7. Crear relaciones tipo-equipo-producto
    equipo_rel1 = TipoEquipoProducto.objects.create(tipo_equipo=equipo1, relacion_producto=prod_rel1)
    equipo_rel2 = TipoEquipoProducto.objects.create(tipo_equipo=equipo2, relacion_producto=prod_rel1)
    equipo_rel3 = TipoEquipoProducto.objects.create(tipo_equipo=equipo2, relacion_producto=prod_rel3)
    equipo_rel4 = TipoEquipoProducto.objects.create(tipo_equipo=equipo3, relacion_producto=prod_rel4)
    
    # 8. Crear tecnologías
    tech1 = Tecnologia.objects.create(name="TechTest Solo")       # Solo tendrá equipo1 (será eliminado)
    tech2 = Tecnologia.objects.create(name="TechTest Compartido") # Tendrá equipo1 y equipo2 (se mantendrá)
    tech3 = Tecnologia.objects.create(name="TechTest Permanente") # Solo tendrá equipo3 (se mantendrá)
    
    # 9. Crear relaciones tecnología-tipo-equipo
    TecnologiaTipoEquipo.objects.create(tecnologia=tech1, relacion_tipo_equipo=equipo_rel1)
    TecnologiaTipoEquipo.objects.create(tecnologia=tech2, relacion_tipo_equipo=equipo_rel1)
    TecnologiaTipoEquipo.objects.create(tecnologia=tech2, relacion_tipo_equipo=equipo_rel3)
    TecnologiaTipoEquipo.objects.create(tecnologia=tech3, relacion_tipo_equipo=equipo_rel4)
    
    print("✅ Estructura de datos creada:")
    print(f"   📋 Criticidades: {Criticidad.objects.filter(name__startswith='CritTest').count()}")
    print(f"   📋 Tipos de Criticidad: {TipoCriticidad.objects.filter(name__startswith='TipoTest').count()}")
    print(f"   📋 Productos: {Producto.objects.filter(name__startswith='ProdTest').count()}")
    print(f"   📋 Tipos de Equipo: {TipoEquipo.objects.filter(name__startswith='EquipoTest').count()}")
    print(f"   📋 Tecnologías: {Tecnologia.objects.filter(name__startswith='TechTest').count()}")
    
    print("\n🎯 Casos de prueba disponibles:")
    print("   1. Eliminar 'TipoTest Eliminable' completo:")
    print("      - Eliminará: ProdTest Solo, EquipoTest Solo, TechTest Solo")
    print("      - Mantendrá: ProdTest Compartido, EquipoTest Compartido, TechTest Compartido")
    print("      - Mantendrá: ProdTest Permanente, EquipoTest Permanente, TechTest Permanente")
    
    print("\n   2. Eliminar solo relación 'TipoTest Eliminable - CritTest Alpha':")
    print("      - Mantendrá: TipoTest Eliminable (tendrá relación con CritTest Beta)")
    print("      - Eliminará: algunos productos/equipos/tecnologías si quedan sin relaciones")
    
    print("\n🌐 Navega a: http://127.0.0.1:8000/complementos/tipo_criticidad/")
    print("🧪 Prueba los botones de eliminar en las filas de TipoTest")

if __name__ == "__main__":
    create_test_data()
