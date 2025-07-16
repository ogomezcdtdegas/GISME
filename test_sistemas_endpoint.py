#!/usr/bin/env python
"""
Script para probar el endpoint de sistemas
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_sistemas_endpoint():
    """Probar el endpoint de sistemas"""
    client = Client()
    
    # Crear usuario de prueba si no existe
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_user',
            password='testpass123',
            email='test@example.com'
        )
    
    # Login
    client.login(username='test_user', password='testpass123')
    
    # Hacer la petición al endpoint
    response = client.get('/complementos/listar-todo-sistemas/')
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.get('content-type', 'N/A')}")
    
    if response.status_code == 200:
        try:
            import json
            data = json.loads(response.content)
            print(f"Sistemas encontrados: {len(data.get('results', []))}")
            print("✅ Endpoint funcionando correctamente")
            
            # Mostrar algunos sistemas de ejemplo
            sistemas = data.get('results', [])
            if sistemas:
                print("\nPrimeros 3 sistemas:")
                for i, sistema in enumerate(sistemas[:3]):
                    print(f"  {i+1}. {sistema.get('tag', 'N/A')} - {sistema.get('ubicacion_nombre', 'N/A')}")
            else:
                print("⚠️  No hay sistemas en la base de datos")
                
        except json.JSONDecodeError as e:
            print(f"❌ Error decodificando JSON: {e}")
            print(f"Contenido: {response.content[:200]}...")
    else:
        print(f"❌ Error en la petición: {response.status_code}")
        print(f"Contenido: {response.content[:200]}...")

if __name__ == '__main__':
    test_sistemas_endpoint()
