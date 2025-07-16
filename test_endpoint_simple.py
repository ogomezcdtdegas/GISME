"""
Script para probar el endpoint de sistemas usando Django shell
"""
import requests
import json

def test_sistemas_endpoint():
    """Probar el endpoint de sistemas"""
    
    # URL del endpoint
    url = 'http://127.0.0.1:8000/complementos/listar-todo-sistemas/'
    
    try:
        # Hacer petición GET
        print(f"🔍 Probando endpoint: {url}")
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                sistemas = data.get('results', []) if 'results' in data else data
                print(f"✅ Sistemas encontrados: {len(sistemas)}")
                
                # Mostrar algunos sistemas de ejemplo
                if sistemas:
                    print("\nPrimeros 3 sistemas:")
                    for i, sistema in enumerate(sistemas[:3]):
                        print(f"  {i+1}. {sistema.get('tag', 'N/A')} - {sistema.get('ubicacion_nombre', 'N/A')}")
                else:
                    print("⚠️  No hay sistemas en la base de datos")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Contenido: {response.text[:200]}...")
        else:
            print(f"❌ Error en la petición: {response.status_code}")
            print(f"Contenido: {response.text[:200]}...")
            
    except requests.ConnectionError:
        print("❌ Error de conexión. ¿Está ejecutándose el servidor Django?")
        print("   Ejecuta: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    test_sistemas_endpoint()
