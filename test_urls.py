#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

print("Probando todas las URLs de TipoCriticidad...")

try:
    # Importar los módulos como lo hace urls.py
    from _AppComplementos.views.views_tipoCriticidad.Queries import GetAllTipoCriticidadPagQuery, GetAllTipoCriticidadListQuery
    from _AppComplementos.views.views_tipoCriticidad.Commands import CreateTipoCriticidadCommand, UpdateTipoCriticidadCommand, DeleteTipoCriticidadCommand
    from _AppComplementos.views.views_tipoCriticidad.Commands.DeleteTipoCriticidadRelacionCommand.DeleteTipoCriticidadRelacionCommand import DeleteTipoCriticidadRelacionCommand
    
    print("✅ Importaciones de URLs exitosas")
    
    # Verificar que las vistas se pueden instanciar
    view1 = GetAllTipoCriticidadPagQuery()
    view2 = GetAllTipoCriticidadListQuery.TipoCriticidadListAllView()
    
    print("✅ Vistas instanciadas correctamente")
    print(f"  - GetAllTipoCriticidadPagQuery: {type(view1)}")
    print(f"  - GetAllTipoCriticidadListQuery: {type(view2)}")
    
    print("✅ Todas las verificaciones de URLs exitosas")
    
except Exception as e:
    print(f"❌ Error en URLs: {e}")
    import traceback
    traceback.print_exc()
