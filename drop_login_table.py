import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.db import connection

cursor = connection.cursor()

print("Eliminando tabla _AppAuth_userloginlog...")
try:
    cursor.execute("DROP TABLE IF EXISTS \"_AppAuth_userloginlog\" CASCADE;")
    print("✅ Tabla eliminada exitosamente")
except Exception as e:
    print(f"❌ Error eliminando tabla: {e}")

print("Proceso completado.")