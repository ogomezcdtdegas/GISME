"""
Script de prueba para verificar que la agrupación de Tipo de Criticidad funciona correctamente
después de las correcciones en el backend.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(r'd:\EQ-456\Escritorio\GISME')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppComplementos.models import Criticidad, TipoCriticidad, TipoCriticidadCriticidad
from _AppComplementos.serializers import TipoCriticidadCriticidadSerializer
from _AppComplementos.views.views_tipoCriticidad.Queries.GetAllTipoCriticidadPagQuery.GetAllTipoCriticidadPagQuery import allTipCriticidadPag

def test_backend_grouping():
    """Prueba que el backend esté enviando los datos correctos para la agrupación"""
    print("🔹 Iniciando prueba de agrupación del backend...")
    
    # 1. Crear datos de prueba
    print("\n1. Creando datos de prueba...")
    
    # Limpiar datos de prueba previos
    TipoCriticidadCriticidad.objects.filter(criticidad__name__startswith="Criticidad Test").delete()
    TipoCriticidad.objects.filter(name__startswith="Tipo Test").delete()
    Criticidad.objects.filter(name__startswith="Criticidad Test").delete()
    
    # Crear criticidades
    criticidad1 = Criticidad.objects.create(name="Criticidad Test 1")
    criticidad2 = Criticidad.objects.create(name="Criticidad Test 2")
    
    # Crear tipos de criticidad
    tipo1 = TipoCriticidad.objects.create(name="Tipo Test 1")
    tipo2 = TipoCriticidad.objects.create(name="Tipo Test 2")
    tipo3 = TipoCriticidad.objects.create(name="Tipo Test 3")
    
    # Crear relaciones - Criticidad1 tiene 2 tipos, Criticidad2 tiene 1 tipo
    rel1 = TipoCriticidadCriticidad.objects.create(criticidad=criticidad1, tipo_criticidad=tipo1)
    rel2 = TipoCriticidadCriticidad.objects.create(criticidad=criticidad1, tipo_criticidad=tipo2)
    rel3 = TipoCriticidadCriticidad.objects.create(criticidad=criticidad2, tipo_criticidad=tipo3)
    
    print(f"✅ Creadas 2 criticidades y 3 tipos de criticidad")
    print(f"✅ Criticidad1 tiene {TipoCriticidadCriticidad.objects.filter(criticidad=criticidad1).count()} relaciones")
    print(f"✅ Criticidad2 tiene {TipoCriticidadCriticidad.objects.filter(criticidad=criticidad2).count()} relaciones")
    
    # 2. Probar la query del backend
    print("\n2. Probando la query del backend...")
    
    view = allTipCriticidadPag()
    queryset = view.get_queryset()
    
    print(f"✅ Query ejecutada, {queryset.count()} registros encontrados")
    
    # 3. Verificar las anotaciones
    print("\n3. Verificando anotaciones 'total_relations'...")
    
    for obj in queryset:
        print(f"Criticidad: {obj.criticidad.name}, Tipo: {obj.tipo_criticidad.name}, Total Relations: {obj.total_relations}")
    
    # 4. Probar el serializer
    print("\n4. Probando el serializer...")
    
    serializer = TipoCriticidadCriticidadSerializer(queryset, many=True)
    data = serializer.data
    
    print(f"✅ Serializer ejecutado, {len(data)} registros serializados")
    
    for item in data:
        print(f"Criticidad: {item['criticidad_name']}, Tipo: {item['tipo_criticidad_name']}, Total Relations: {item['total_relations']}")
    
    # 5. Verificar la agrupación esperada
    print("\n5. Verificando agrupación esperada...")
    
    # Agrupar por criticidad
    grouped = {}
    for item in data:
        criticidad = item['criticidad_name']
        if criticidad not in grouped:
            grouped[criticidad] = []
        grouped[criticidad].append(item)
    
    print(f"✅ Agrupación por criticidad:")
    for criticidad, items in grouped.items():
        print(f"  - {criticidad}: {len(items)} relaciones")
        for item in items:
            print(f"    └─ {item['tipo_criticidad_name']} (total_relations: {item['total_relations']})")
    
    # 6. Verificar que total_relations es consistente
    print("\n6. Verificando consistencia de total_relations...")
    
    inconsistent = False
    for criticidad, items in grouped.items():
        expected_total = len(items)
        for item in items:
            if item['total_relations'] != expected_total:
                print(f"❌ ERROR: {criticidad} - {item['tipo_criticidad_name']} tiene total_relations={item['total_relations']}, esperado={expected_total}")
                inconsistent = True
    
    if not inconsistent:
        print("✅ Todas las anotaciones 'total_relations' son consistentes")
    
    # 7. Limpiar datos de prueba
    print("\n7. Limpiando datos de prueba...")
    
    TipoCriticidadCriticidad.objects.filter(criticidad__in=[criticidad1, criticidad2]).delete()
    TipoCriticidad.objects.filter(id__in=[tipo1.id, tipo2.id, tipo3.id]).delete()
    Criticidad.objects.filter(id__in=[criticidad1.id, criticidad2.id]).delete()
    
    print("✅ Datos de prueba eliminados")
    
    print("\n🎉 Prueba completada")
    
    return not inconsistent

if __name__ == "__main__":
    success = test_backend_grouping()
    if success:
        print("\n✅ ÉXITO: El backend está enviando los datos correctos para la agrupación")
    else:
        print("\n❌ ERROR: El backend no está enviando los datos correctos")
    
    sys.exit(0 if success else 1)
