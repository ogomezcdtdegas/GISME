import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Validar SECRET_KEY
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("No se ha configurado la SECRET_KEY para la aplicación Django")

NODE_RED_TOKEN = os.getenv("NODE_RED_TOKEN")

NODE_RED_USER = os.getenv("NODE_RED_USER")
NODE_RED_PASS = os.getenv("NODE_RED_PASS")

# Configuraciones de cookies seguras

# Esta configuración asegura que la cookie de sesión solo sea accesible por el servidor y no por scripts del lado del cliente (como JavaScript). 
# Esto ayuda a prevenir ataques de cross-site scripting (XSS), donde un atacante podría intentar robar la cookie de sesión para hacerse pasar por el usuario.
SESSION_COOKIE_HTTPONLY = True

# Similar a SESSION_COOKIE_HTTPONLY, esta configuración hace que la cookie CSRF (utilizada para proteger contra ataques de falsificación de solicitudes entre sitios) no sea accesible por JavaScript. 
# Aunque es menos común habilitarla (ya que algunos frameworks pueden necesitar acceso a esta cookie), activarla incrementa la seguridad al reducir la superficie de ataque en caso de vulnerabilidades XSS.
CSRF_COOKIE_HTTPONLY = True

# Esta configuración controla cómo se envían las cookies de sesión en solicitudes entre sitios. El valor 'Lax' permite que la cookie se envíe en solicitudes GET seguras (como navegaciones de nivel superior), pero bloquea su envío en solicitudes POST o de otros métodos desde sitios externos. 
# Esto ayuda a mitigar ataques CSRF al limitar el envío de cookies a contextos confiables. El valor 'Strict' sería aún más restrictivo, pero podría afectar la experiencia del usuario.
SESSION_COOKIE_SAMESITE = 'Lax'

# Similar a SESSION_COOKIE_SAMESITE, esta configuración aplica la política SameSite a la cookie CSRF. Al establecerla en 'Lax', se asegura que la cookie CSRF solo se envíe en solicitudes seguras entre sitios, reduciendo el riesgo de ataques CSRF. 
# Usar 'Lax' es un buen equilibrio entre seguridad y usabilidad, pero puedes considerar 'Strict' si tu aplicación no depende de solicitudes entre sitios
CSRF_COOKIE_SAMESITE = 'Lax'

# Protección contra clickjacking
X_FRAME_OPTIONS = 'DENY'
# Esta configuración establece el encabezado HTTP 'X-Frame-Options' en 'DENY', lo que indica a los navegadores que no permitan que las páginas de tu aplicación Django se carguen dentro de un <iframe>, <frame>, <object>, <embed> o <applet> en ningún sitio web, incluido el tuyo propio.
# Propósito: Previene ataques de clickjacking, un tipo de ataque en el que un sitio malicioso incrusta tu página en un iframe invisible y engaña a los usuarios para que realicen acciones no deseadas (como hacer clic en botones ocultos) mientras creen que están interactuando con el sitio malicioso.
# Cómo funciona: Al establecer 'DENY', cualquier intento de cargar tu sitio en un iframe será bloqueado por el navegador, mostrando un error o simplemente no renderizando el contenido. Esto asegura que tu aplicación no pueda ser manipulada por sitios externos que intenten superponerla con contenido malicioso.
# Opciones alternativas:
#   - 'SAMEORIGIN': Permite que las páginas se carguen en iframes solo si provienen del mismo dominio (por ejemplo, tu propio sitio). Útil si necesitas iframes internamente, pero sigue bloqueando sitios externos.
#   - 'ALLOW-FROM <uri>': Permite iframes solo desde un dominio específico, aunque esta opción está obsoleta en muchos navegadores modernos.
# Consideraciones:
#   - 'DENY' es la opción más segura, pero puede ser restrictiva si tu aplicación necesita cargar páginas en iframes (por ejemplo, para widgets o integraciones internas). En tales casos, considera 'SAMEORIGIN' o usa una política de Content Security Policy (CSP) más granular con la directiva 'frame-ancestors'.
#   - Ya tienes 'django.middleware.clickjacking.XFrameOptionsMiddleware' en tu lista de MIDDLEWARE, lo que asegura que el encabezado 'X-Frame-Options' se aplique a todas las respuestas HTTP. Sin este middleware, la configuración de X_FRAME_OPTIONS no tendría efecto.
#   - Para una protección más avanzada contra clickjacking, considera combinar esta configuración con una política CSP (por ejemplo, `frame-ancestors 'self'`) para tener un control más fino sobre qué dominios pueden incrustar tu sitio.
# Impacto: Esta configuración es una defensa crítica contra clickjacking, especialmente en aplicaciones que manejan datos sensibles o sesiones autenticadas, ya que asegura que los usuarios interactúen directamente con tu sitio y no con una versión incrustada manipulada.
# Nota: Si tu aplicación depende de iframes para ciertas funcionalidades (como paneles de administración embebidos o integraciones de terceros), prueba exhaustivamente después de activar 'DENY' para evitar romper características legítimas.

# Tiempo de vida de sesión (segundos) y renovación por request
SESSION_COOKIE_AGE = 1200           # 20 minutos
SESSION_SAVE_EVERY_REQUEST = True   # renueva el vencimiento con cada reques

# Evita que el navegador intente adivinar tipos de contenido, mitigando ataques de MIME sniffing.
SECURE_CONTENT_TYPE_NOSNIFF = True
#Los navegadores, cuando reciben un archivo, deberían usar el Content-Type indicado en la cabecera HTTP para saber qué tipo de contenido es (ej. text/html, image/png, application/json).
#Pero algunos navegadores antiguos o mal configurados intentan “adivinar” (sniff) el tipo de archivo si la cabecera no está clara, para mostrarlo “bonito” al usuario.
#Problema:
#Un atacante puede subir un archivo aparentemente inofensivo (ejemplo: foto.png), pero que en realidad contiene código HTML o JavaScript malicioso.
#Si el navegador “olfatea” y lo interpreta como text/html, podría ejecutar ese código dentro de tu dominio → XSS (Cross-Site Scripting).

SECURE_REFERRER_POLICY = "same-origin"
# Limita la info del Referer a tu mismo origen para reducir fuga de datos en enlaces externos.

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    '_AppHome',
    '_AppMonitoreoCoriolis',
    '_AppCalc1',
    '_AppCalc2',
    '_AppCommon',
    '_AppHerramientas',
    '_AppComplementos',
    '_AppAuth',
    '_AppAdmin',
    'django_extensions',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    '_AppAuth.middleware_msal.MSALAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    '_AppAuth.middleware.AuthMiddleware',
]

USE_EASYAUTH = os.getenv("USE_EASYAUTH", "False").lower() == "true"

# MSAL Configuration for Azure AD authentication (all environments)
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_REDIRECT_URI = os.getenv("AZURE_REDIRECT_URI")
AZURE_SCOPES = [s.strip() for s in os.getenv("AZURE_SCOPES", "openid,profile,email,offline_access").split(",") if s.strip()]

'''
if USE_EASYAUTH:
    LOGIN_URL = "/.auth/login/aad?prompt=login&amr_values=mfa&post_login_redirect_uri=/"
    LOGOUT_REDIRECT_URL = "/.auth/logout?post_logout_redirect_uri=/"
else:
    # 🔁 Ahora el login local será por MSAL
    LOGIN_URL = "/aad/login"
    LOGOUT_REDIRECT_URL = "/aad/logout"
'''

if USE_EASYAUTH:
    # ✅ sin amr_values (permitidos: post_login_redirect_uri, prompt, domain_hint, login_hint)
    LOGIN_URL = "/.auth/login/aad?prompt=login&post_login_redirect_uri=/"
    LOGOUT_REDIRECT_URL = "/.auth/logout?post_logout_redirect_uri=/"
else:
    # MSAL authentication - URLs directas que coinciden con Azure AD registration
    LOGIN_URL = "/aad/login"
    LOGOUT_REDIRECT_URL = "/aad/logout"
    
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "config/templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Para archivos estáticos globales
    os.path.join(BASE_DIR, 'config/static')  # Para archivos estáticos de configuración
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ),
}

