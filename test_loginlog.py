#!/usr/bin/env python
"""
Script de prueba para verificar que la tabla UserLoginLog funciona
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from _AppAuth.models import UserLoginLog
from django.contrib.auth import get_user_model

User = get_user_model()

def test_userloginlog():
    print("🔍 Probando modelo UserLoginLog...")
    
    # Verificar que el modelo se puede importar
    print("✅ Modelo UserLoginLog importado correctamente")
    
    # Verificar que la tabla existe consultando
    try:
        count = UserLoginLog.objects.count()
        print(f"✅ Tabla existe. Registros actuales: {count}")
    except Exception as e:
        print(f"❌ Error accediendo a la tabla: {e}")
        return False
    
    # Verificar usuarios disponibles
    user_count = User.objects.count()
    print(f"📊 Usuarios en el sistema: {user_count}")
    
    if user_count > 0:
        # Crear un registro de prueba
        try:
            first_user = User.objects.first()
            test_log = UserLoginLog.objects.create(
                user=first_user,
                email=first_user.email or "test@example.com",
                ip_address="127.0.0.1"
            )
            print(f"✅ Registro de prueba creado: {test_log}")
            
            # Listar todos los registros
            all_logs = UserLoginLog.objects.all()
            print(f"📋 Registros totales después del test: {all_logs.count()}")
            
            return True
        except Exception as e:
            print(f"❌ Error creando registro de prueba: {e}")
            return False
    else:
        print("⚠️ No hay usuarios en el sistema para probar")
        return True

if __name__ == "__main__":
    success = test_userloginlog()
    if success:
        print("\n🎉 ¡Test completado exitosamente!")
    else:
        print("\n❌ Test falló")