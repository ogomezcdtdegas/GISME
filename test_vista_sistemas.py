#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.test import RequestFactory
from _AppComplementos.views.views_Sistema.Queries.GetAllSistemasQuery.GetAllSistemasQuery import ListarTodosSistemasQueryView

def test_listar_todos_sistemas():
    print("🔍 Testing ListarTodosSistemasQueryView...")
    
    # Crear una request factory
    factory = RequestFactory()
    request = factory.get('/complementos/listar-todo-sistemas/')
    request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'  # Simular AJAX
    
    # Crear instancia de la vista
    view = ListarTodosSistemasQueryView()
    
    try:
        # Probar la vista
        response = view.get(request)
        print(f"✅ Vista funcionó correctamente")
        print(f"📊 Status code: {response.status_code}")
        print(f"📋 Response data type: {type(response.data)}")
        if hasattr(response, 'data'):
            if 'success' in response.data:
                print(f"🎯 Success: {response.data['success']}")
            if 'count' in response.data:
                print(f"📈 Count: {response.data['count']}")
            if 'data' in response.data:
                print(f"📦 Data items: {len(response.data['data'])}")
        return True
    except Exception as e:
        print(f"❌ Error en la vista: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_listar_todos_sistemas()
