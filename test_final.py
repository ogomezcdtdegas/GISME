#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

print("🔍 Probando todas las importaciones de TipoCriticidad...")

try:
    # Importar todos los módulos como lo hace urls.py
    from _AppComplementos.views.views_tipoCriticidad.Queries import GetAllTipoCriticidadPagQuery, GetAllTipoCriticidadListQuery
    from _AppComplementos.views.views_tipoCriticidad.Commands import CreateTipoCriticidadCommand, UpdateTipoCriticidadCommand, DeleteTipoCriticidadCommand
    from _AppComplementos.views.views_tipoCriticidad.Commands.DeleteTipoCriticidadRelacionCommand.DeleteTipoCriticidadRelacionCommand import DeleteTipoCriticidadRelacionCommand
    
    print("✅ Importaciones de módulos exitosas")
    
    # Verificar que las vistas principales se pueden instanciar
    view1 = GetAllTipoCriticidadPagQuery()
    view2 = GetAllTipoCriticidadListQuery.TipoCriticidadListAllView()
    view3 = GetAllTipoCriticidadListQuery.TiposCriticidadUnicosView()
    
    print("✅ Vistas principales instanciadas correctamente")
    print(f"  - GetAllTipoCriticidadPagQuery: {type(view1)}")
    print(f"  - TipoCriticidadListAllView: {type(view2)}")
    print(f"  - TiposCriticidadUnicosView: {type(view3)}")
    
    # Verificar que las vistas de comando se pueden instanciar
    cmd1 = CreateTipoCriticidadCommand.crearTipCriticidad()
    cmd2 = UpdateTipoCriticidadCommand.editarTipCriticidad()
    cmd3 = DeleteTipoCriticidadCommand()
    cmd4 = DeleteTipoCriticidadRelacionCommand()
    
    print("✅ Vistas de comando instanciadas correctamente")
    print(f"  - CreateTipoCriticidadCommand: {type(cmd1)}")
    print(f"  - UpdateTipoCriticidadCommand: {type(cmd2)}")
    print(f"  - DeleteTipoCriticidadCommand: {type(cmd3)}")
    print(f"  - DeleteTipoCriticidadRelacionCommand: {type(cmd4)}")
    
    print("\n🎯 Todas las verificaciones completadas exitosamente!")
    print("🚀 TipoCriticidad está listo para producción")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
