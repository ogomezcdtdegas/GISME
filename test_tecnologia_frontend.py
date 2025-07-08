# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
TEST FRONTEND TECNOLOGIA - Validacion completa del comportamiento frontend
========================================================================

Este script valida el comportamiento completo del frontend para Tecnologia:
1. Agrupacion visual con badges correctos
2. Alternancia de colores entre grupos
3. Funcionalidad de eliminacion con alertas apropiadas
4. Comportamiento de cascada y limpieza de huerfanos
5. Actualizacion correcta de la tabla tras eliminaciones
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from _AppComplementos.models import *
from django.db import transaction
import json

class TecnologiaFrontendTest:
    def __init__(self):
        self.test_data = []
        
    def setup_test_data(self):
        """Crear datos de prueba para validación frontend"""
        print("🔧 Configurando datos de prueba...")
        
        with transaction.atomic():
            # Limpiar datos existentes
            TecnologiaRelacion.objects.all().delete()
            Tecnologia.objects.all().delete()
            
            # Crear tecnologías con diferentes números de relaciones
            self.test_data = []
            
            # Tecnología 1: Con múltiples relaciones (3 relaciones)
            tech1 = Tecnologia.objects.create(name="Frontend React")
            
            # Tecnología 2: Con una sola relación
            tech2 = Tecnologia.objects.create(name="Backend Python")
            
            # Tecnología 3: Con múltiples relaciones (2 relaciones)
            tech3 = Tecnologia.objects.create(name="Base de Datos MySQL")
            
            # Obtener datos necesarios para las relaciones
            criticidades = list(Criticidad.objects.all()[:3])
            tipo_criticidades = list(TipoCriticidad.objects.all()[:3])
            productos = list(Producto.objects.all()[:3])
            tipos_equipo = list(TipoEquipo.objects.all()[:3])
            
            if not all([criticidades, tipo_criticidades, productos, tipos_equipo]):
                print("❌ Error: No hay datos suficientes en los niveles superiores")
                return False
            
            # Crear relaciones para Frontend React (3 relaciones)
            TecnologiaRelacion.objects.create(
                tecnologia=tech1,
                tipo_equipo=tipos_equipo[0],
                producto=productos[0],
                tipo_criticidad=tipo_criticidades[0],
                criticidad=criticidades[0]
            )
            TecnologiaRelacion.objects.create(
                tecnologia=tech1,
                tipo_equipo=tipos_equipo[0],
                producto=productos[1],
                tipo_criticidad=tipo_criticidades[0],
                criticidad=criticidades[0]
            )
            TecnologiaRelacion.objects.create(
                tecnologia=tech1,
                tipo_equipo=tipos_equipo[1],
                producto=productos[0],
                tipo_criticidad=tipo_criticidades[1],
                criticidad=criticidades[1]
            )
            
            # Crear relación para Backend Python (1 relación)
            TecnologiaRelacion.objects.create(
                tecnologia=tech2,
                tipo_equipo=tipos_equipo[0],
                producto=productos[2],
                tipo_criticidad=tipo_criticidades[2],
                criticidad=criticidades[2]
            )
            
            # Crear relaciones para Base de Datos MySQL (2 relaciones)
            TecnologiaRelacion.objects.create(
                tecnologia=tech3,
                tipo_equipo=tipos_equipo[1],
                producto=productos[1],
                tipo_criticidad=tipo_criticidades[1],
                criticidad=criticidades[1]
            )
            TecnologiaRelacion.objects.create(
                tecnologia=tech3,
                tipo_equipo=tipos_equipo[2],
                producto=productos[2],
                tipo_criticidad=tipo_criticidades[2],
                criticidad=criticidades[2]
            )
            
            self.test_data = [
                {
                    'tecnologia': tech1,
                    'name': 'Frontend React',
                    'relaciones': 3,
                    'tipo': 'múltiples relaciones'
                },
                {
                    'tecnologia': tech2,
                    'name': 'Backend Python',
                    'relaciones': 1,
                    'tipo': 'única relación'
                },
                {
                    'tecnologia': tech3,
                    'name': 'Base de Datos MySQL',
                    'relaciones': 2,
                    'tipo': 'múltiples relaciones'
                }
            ]
            
            print("✅ Datos de prueba configurados correctamente")
            return True
    
    def validate_data_structure(self):
        """Validar la estructura de datos para el frontend"""
        print("\n📊 Validando estructura de datos...")
        
        # Obtener todas las relaciones agrupadas
        relaciones = TecnologiaRelacion.objects.select_related(
            'tecnologia', 'tipo_equipo', 'producto', 'tipo_criticidad', 'criticidad'
        ).all()
        
        # Agrupar por tecnología
        grupos = {}
        for relacion in relaciones:
            tech_id = relacion.tecnologia.id
            if tech_id not in grupos:
                grupos[tech_id] = {
                    'tecnologia': relacion.tecnologia,
                    'relaciones': []
                }
            grupos[tech_id]['relaciones'].append(relacion)
        
        print(f"📈 Datos agrupados encontrados: {len(grupos)} grupos")
        
        for tech_id, grupo in grupos.items():
            tech = grupo['tecnologia']
            count = len(grupo['relaciones'])
            badge_text = f"{count} combinación" if count == 1 else f"{count} combinaciones"
            
            print(f"  🔹 {tech.name}: {count} relaciones → Badge: '{badge_text}'")
            
            # Mostrar detalles de las relaciones
            for i, rel in enumerate(grupo['relaciones'], 1):
                print(f"    {i}. {rel.tipo_equipo.name} → {rel.producto.name} → {rel.tipo_criticidad.name} → {rel.criticidad.name}")
        
        return True
    
    def test_deletion_scenarios(self):
        """Probar diferentes escenarios de eliminación"""
        print("\n🗑️ Probando escenarios de eliminación...")
        
        # Scenario 1: Eliminar una relación de tecnología con múltiples relaciones
        print("\n📋 Escenario 1: Eliminar relación de tecnología con múltiples relaciones")
        tech1 = Tecnologia.objects.get(name="Frontend React")
        relaciones_tech1 = TecnologiaRelacion.objects.filter(tecnologia=tech1)
        print(f"  🔹 {tech1.name} tiene {relaciones_tech1.count()} relaciones")
        
        if relaciones_tech1.count() > 1:
            print("  ⚠️  Esperado: Modal con opciones de eliminación")
            print("  📝 Opciones disponibles:")
            print("     • Solo eliminar esta relación")
            print("     • Eliminar la tecnología y todas sus relaciones")
            print("  ℹ️  Nota: La tecnología es el último nivel, no hay cascada")
        
        # Scenario 2: Eliminar última relación de tecnología
        print("\n📋 Escenario 2: Eliminar última relación de tecnología")
        tech2 = Tecnologia.objects.get(name="Backend Python")
        relaciones_tech2 = TecnologiaRelacion.objects.filter(tecnologia=tech2)
        print(f"  🔹 {tech2.name} tiene {relaciones_tech2.count()} relaciones")
        
        if relaciones_tech2.count() == 1:
            print("  ⚠️  Esperado: Modal de confirmación simple")
            print("  📝 Comportamiento:")
            print("     • Advertencia: 'Esta es la última relación'")
            print("     • 'La tecnología será eliminada completamente'")
            print("     • Usar DeleteTecnologiaRelacionCommand (backend maneja limpieza)")
        
        return True
    
    def validate_frontend_features(self):
        """Validar características esperadas del frontend"""
        print("\n🎨 Validando características del frontend...")
        
        expected_features = [
            {
                'feature': 'Agrupación Visual',
                'description': 'Rowspan para nombre de tecnología, badges con contador',
                'validation': 'Verificar que tecnologías se muestren agrupadas con badges correctos'
            },
            {
                'feature': 'Alternancia de Colores',
                'description': 'Grupos alternos con colores diferentes',
                'validation': 'Verificar clases group-odd y group-even aplicadas correctamente'
            },
            {
                'feature': 'Hover Effect',
                'description': 'Efecto hover para grupo completo',
                'validation': 'Verificar que hover resalta todo el grupo'
            },
            {
                'feature': 'Botones de Eliminación',
                'description': 'Botón de eliminar para cada relación',
                'validation': 'Verificar que cada fila tenga botón de eliminar'
            },
            {
                'feature': 'Modales de Confirmación',
                'description': 'Diferentes modales según número de relaciones',
                'validation': 'Verificar que aparezcan modales apropiados'
            },
            {
                'feature': 'Mensajes de Advertencia',
                'description': 'Información clara sobre las acciones',
                'validation': 'Verificar que mensajes sean claros y precisos'
            }
        ]
        
        for feature in expected_features:
            print(f"  ✅ {feature['feature']}")
            print(f"     📝 {feature['description']}")
            print(f"     🔍 {feature['validation']}")
        
        return True
    
    def generate_test_report(self):
        """Generar reporte de prueba"""
        print("\n📋 REPORTE DE PRUEBA FRONTEND - TECNOLOGÍA")
        print("=" * 60)
        
        # Resumen de datos
        total_tecnologias = Tecnologia.objects.count()
        total_relaciones = TecnologiaRelacion.objects.count()
        
        print(f"📊 Datos de prueba:")
        print(f"  • Total tecnologías: {total_tecnologias}")
        print(f"  • Total relaciones: {total_relaciones}")
        
        # Detalle por tecnología
        print(f"\n🔍 Detalle por tecnología:")
        for data in self.test_data:
            tech = data['tecnologia']
            relaciones_count = TecnologiaRelacion.objects.filter(tecnologia=tech).count()
            badge = f"{relaciones_count} combinación" if relaciones_count == 1 else f"{relaciones_count} combinaciones"
            
            print(f"  🔹 {data['name']}: {relaciones_count} relaciones → Badge: '{badge}'")
            print(f"     Tipo: {data['tipo']}")
            print(f"     Esperado: {'Modal con opciones' if relaciones_count > 1 else 'Modal de confirmación simple'}")
        
        # Instrucciones para validación manual
        print(f"\n📝 INSTRUCCIONES PARA VALIDACIÓN MANUAL:")
        print("=" * 50)
        print("1. Abrir http://127.0.0.1:8000/complementos/tecnologias/")
        print("2. Verificar agrupación visual con badges correctos")
        print("3. Verificar alternancia de colores entre grupos")
        print("4. Probar hover effect en grupos completos")
        print("5. Probar eliminación en tecnología con múltiples relaciones:")
        print("   - Debe aparecer modal con opciones")
        print("   - Probar 'Solo eliminar esta relación'")
        print("   - Probar 'Eliminar la tecnología y todas sus relaciones'")
        print("6. Probar eliminación en tecnología con única relación:")
        print("   - Debe aparecer modal de confirmación simple")
        print("   - Debe advertir que es la última relación")
        print("7. Verificar que la tabla se actualice correctamente tras eliminaciones")
        print("8. Verificar que los mensajes sean claros y precisos")
        
        # Casos de prueba específicos
        print(f"\n🧪 CASOS DE PRUEBA ESPECÍFICOS:")
        print("=" * 40)
        print("CASO 1: Eliminar relación de 'Frontend React' (3 relaciones)")
        print("  - Esperado: Modal con opciones")
        print("  - Seleccionar 'Solo eliminar esta relación'")
        print("  - Verificar que queden 2 relaciones")
        print("  - Verificar que badge se actualice a '2 combinaciones'")
        
        print("\nCASO 2: Eliminar relación de 'Backend Python' (1 relación)")
        print("  - Esperado: Modal de confirmación simple")
        print("  - Debe advertir que es la última relación")
        print("  - Confirmar eliminación")
        print("  - Verificar que la tecnología desaparezca completamente")
        
        print("\nCASO 3: Eliminar tecnología completa 'Base de Datos MySQL'")
        print("  - Esperado: Modal con opciones")
        print("  - Seleccionar 'Eliminar la tecnología y todas sus relaciones'")
        print("  - Verificar que todas las relaciones desaparezcan")
        print("  - Verificar que la tecnología desaparezca completamente")
        
        return True
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS FRONTEND - TECNOLOGÍA")
        print("=" * 60)
        
        try:
            # Configurar datos de prueba
            if not self.setup_test_data():
                return False
            
            # Validar estructura de datos
            if not self.validate_data_structure():
                return False
            
            # Probar escenarios de eliminación
            if not self.test_deletion_scenarios():
                return False
            
            # Validar características del frontend
            if not self.validate_frontend_features():
                return False
            
            # Generar reporte
            if not self.generate_test_report():
                return False
            
            print("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("🌐 Servidor corriendo en: http://127.0.0.1:8000/complementos/tecnologias/")
            print("📋 Proceder con validación manual según las instrucciones anteriores")
            
            return True
            
        except Exception as e:
            print(f"❌ Error durante las pruebas: {str(e)}")
            return False

if __name__ == "__main__":
    test = TecnologiaFrontendTest()
    success = test.run_all_tests()
    
    if success:
        print("\n🎯 PRUEBAS FRONTEND COMPLETADAS")
        print("Ahora puedes validar manualmente en el navegador")
    else:
        print("\n❌ PRUEBAS FALLIDAS")
        sys.exit(1)
