# -*- coding: utf-8 -*-
"""
Script para crear datos de prueba para validacion frontend de Tecnologia
"""

from _AppComplementos.models import *
from django.db import transaction

def create_test_data():
    """Crear datos de prueba para validacion frontend"""
    print("Configurando datos de prueba...")
    
    with transaction.atomic():
        # Limpiar datos existentes
        TecnologiaTipoEquipo.objects.all().delete()
        Tecnologia.objects.all().delete()
        
        # Crear tecnologias con diferentes numeros de relaciones
        tech1 = Tecnologia.objects.create(name="Frontend React")
        tech2 = Tecnologia.objects.create(name="Backend Python")
        tech3 = Tecnologia.objects.create(name="Base de Datos MySQL")
        
        # Obtener relaciones tipo_equipo existentes
        tipo_equipo_relaciones = list(TipoEquipoProducto.objects.all()[:6])
        
        if len(tipo_equipo_relaciones) < 6:
            print("Error: No hay suficientes relaciones TipoEquipo para crear las tecnologias")
            return False
        
        # Crear relaciones para Frontend React (3 relaciones)
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=tipo_equipo_relaciones[0]
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=tipo_equipo_relaciones[1]
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech1,
            relacion_tipo_equipo=tipo_equipo_relaciones[2]
        )
        
        # Crear relacion para Backend Python (1 relacion)
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech2,
            relacion_tipo_equipo=tipo_equipo_relaciones[3]
        )
        
        # Crear relaciones para Base de Datos MySQL (2 relaciones)
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech3,
            relacion_tipo_equipo=tipo_equipo_relaciones[4]
        )
        TecnologiaTipoEquipo.objects.create(
            tecnologia=tech3,
            relacion_tipo_equipo=tipo_equipo_relaciones[5]
        )
        
        print("Datos de prueba configurados correctamente")
        
        # Mostrar resumen
        print("\nResumen de datos creados:")
        print(f"- Frontend React: {TecnologiaTipoEquipo.objects.filter(tecnologia=tech1).count()} relaciones")
        print(f"- Backend Python: {TecnologiaTipoEquipo.objects.filter(tecnologia=tech2).count()} relaciones")
        print(f"- Base de Datos MySQL: {TecnologiaTipoEquipo.objects.filter(tecnologia=tech3).count()} relaciones")
        
        return True

# Ejecutar
if create_test_data():
    print("\nDatos de prueba creados exitosamente")
    print("Abrir: http://127.0.0.1:8000/complementos/tecnologias/")
else:
    print("Error al crear datos de prueba")
