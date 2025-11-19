"""
Middleware para agregar cabeceras Cache Control apropiadas
especialmente para rutas de autenticación y otras rutas críticas
"""
import re


class CacheControlMiddleware:
    """
    Middleware que añade cabeceras Cache Control apropiadas según el tipo de ruta.
    
    Para mayor seguridad:
    - Rutas de auth: no-cache, no-store
    - APIs: no-cache
    - Archivos estáticos: cache largo
    - Páginas dinámicas: cache corto
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Requerido para Django 5.2+
        self.async_mode = False
        
        # Patrones de rutas que NO deben ser cacheadas (por seguridad)
        self.no_cache_patterns = [
            r'^/aad/',          # Rutas AAD auth
            r'^/auth/',         # Rutas auth generales
            r'^/\.auth/',       # Easy Auth routes
            r'^/admin/',        # Admin panel
            r'^/api/',          # API endpoints
            r'^/logout',        # Logout
            r'^/login',         # Login
        ]
        
        # Patrones de archivos estáticos (cache largo)
        self.static_patterns = [
            r'^/static/',
            r'^/staticfiles/',
            r'\.css$',
            r'\.js$',
            r'\.png$',
            r'\.jpg$',
            r'\.jpeg$',
            r'\.gif$',
            r'\.ico$',
            r'\.svg$',
            r'\.woff$',
            r'\.woff2$',
            r'\.ttf$',
        ]
        
        # Compilar patrones regex para mejor rendimiento
        self.no_cache_regex = [re.compile(pattern) for pattern in self.no_cache_patterns]
        self.static_regex = [re.compile(pattern) for pattern in self.static_patterns]
    
    def __call__(self, request):
        """
        Método principal del middleware que procesa la request y response
        """
        response = self.get_response(request)
        return self._process_response(request, response)
    
    def _process_response(self, request, response):
        """
        Procesa la respuesta y añade las cabeceras Cache Control apropiadas
        """
        path = request.path_info
        
        # Si ya tiene Cache-Control, no sobrescribir
        if 'Cache-Control' in response:
            return response
        
        # Verificar si es una ruta que no debe ser cacheada
        if self._should_not_cache(path):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Verificar si es un archivo estático
        elif self._is_static_file(path):
            # Cache largo para archivos estáticos (1 año)
            response['Cache-Control'] = 'public, max-age=31536000, immutable'
        
        # Para el resto de páginas (contenido dinámico)
        else:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
    
    def _should_not_cache(self, path):
        """
        Verifica si una ruta no debe ser cacheada por razones de seguridad
        """
        return any(regex.match(path) for regex in self.no_cache_regex)
    
    def _is_static_file(self, path):
        """
        Verifica si una ruta corresponde a un archivo estático
        """
        return any(regex.search(path) for regex in self.static_regex)