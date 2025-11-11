import requests
import sys

def test_cache_headers():
    """
    Prueba las cabeceras Cache Control en diferentes rutas
    """
    print("Probando cabeceras Cache Control...")
    print("="*50)
    
    # Rutas de prueba
    test_urls = [
        "http://localhost:8000/aad/login?post_login_redirect_uri=/",
        "http://localhost:8000/",
        "http://localhost:8000/static/css/global.css",
        "http://localhost:8000/api/docs/",
        "http://localhost:8000/admin/"
    ]
    
    for url in test_urls:
        try:
            print(f"\nProbando: {url}")
            response = requests.head(url, allow_redirects=False, timeout=5)
            
            print(f"Status: {response.status_code}")
            
            # Cabeceras de cache relevantes
            cache_headers = ['Cache-Control', 'Pragma', 'Expires']
            
            for header in cache_headers:
                if header in response.headers:
                    print(f"{header}: {response.headers[header]}")
                else:
                    print(f"{header}: No presente")
                    
        except requests.exceptions.RequestException as e:
            print(f"Error conectando a {url}: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_cache_headers()