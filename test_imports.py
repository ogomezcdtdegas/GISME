#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

print("Probando importaciones...")

try:
    # Importar todos los componentes necesarios
    from _AppComplementos.views.views_tipoCriticidad.Queries.GetAllTipoCriticidadPagQuery.GetAllTipoCriticidadPagQuery import allTipCriticidadPag
    from _AppComplementos.models import TipoCriticidadCriticidad
    from _AppComplementos.serializers import TipoCriticidadCriticidadSerializer
    
    print("✅ Importaciones exitosas")
    
    # Verificar que la clase está definida correctamente
    view = allTipCriticidadPag()
    print(f"✅ Clase instanciada correctamente: {type(view)}")
    
    # Verificar que los métodos existen
    print(f"✅ Método get_allowed_ordering_fields: {hasattr(view, 'get_allowed_ordering_fields')}")
    print(f"✅ Método apply_search_filters: {hasattr(view, 'apply_search_filters')}")
    
    # Verificar los campos permitidos
    allowed_fields = view.get_allowed_ordering_fields()
    print(f"✅ Campos permitidos: {allowed_fields}")
    
    print("✅ Todas las verificaciones exitosas")
    
except Exception as e:
    print(f"❌ Error en importaciones: {e}")
    import traceback
    traceback.print_exc()
