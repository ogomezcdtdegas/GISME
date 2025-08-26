from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS_PROD', 'tudominio.com').split(',')

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in os.getenv('DJANGO_ALLOWED_HOSTS_PROD', 'tudominio.com').split(',')
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Configuración para Azure App Service Linux
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

''' ---------------------------------------------------------------CONFIGURACIONES DE SEGURIDAD-------------------------------------------------------------------------------------------- '''
# Preparar para HTTPS (comentar hasta que esté configurado)

SECURE_SSL_REDIRECT = True
# Protección contra: Ataques "man-in-the-middle" (MITM) y transmisión de datos en texto plano.
# Explicación: Esta configuración fuerza que todas las solicitudes HTTP se redirijan a HTTPS, asegurando que los datos (como contraseñas, tokens de sesión o información sensible) no se transmitan sin cifrado. Los ataques MITM permiten a un atacante interceptar datos en conexiones no seguras (HTTP), pero HTTPS (con SSL/TLS) cifra los datos, haciéndolos ilegibles para los atacantes.

# Confiar en el proxy para detectar HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Protección contra: Errores de seguridad al usar balanceadores/proxies inversos (Azure, Nginx, Heroku).
# Explicación: Cuando la aplicación está detrás de un proxy, Django recibe las peticiones como HTTP,
# aunque realmente el cliente usó HTTPS. El proxy añade la cabecera "X-Forwarded-Proto" para indicar
# el protocolo original. Con esta configuración, Django interpreta correctamente que la conexión fue
# segura y aplica medidas como cookies seguras (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE) y redirecciones HTTPS.
# Sin esta opción, Django podría pensar que la conexión no es segura, causando fallos en autenticación,
# sesiones y exposición de URLs HTTP en lugar de HTTPS.

SECURE_HSTS_SECONDS = 31536000
# Protección contra: Ataques de degradación de protocolo (protocol downgrade attacks) y conexiones inseguras iniciales.
# Explicación: HSTS (HTTP Strict Transport Security) indica a los navegadores que solo usen HTTPS para conectarse a tu sitio durante un período (1 año en este caso). Esto previene que un atacante engañe al navegador para que use HTTP en lugar de HTTPS (degradación de protocolo) o que los usuarios accedan a tu sitio a través de una conexión no segura en su primera visita.

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# Protección contra: Conexiones inseguras en subdominios y ataques MITM en subdominios.
# Explicación: Extiende la política HSTS a todos los subdominios de tu dominio (por ejemplo, sub.tudominio.com). Esto asegura que cualquier subdominio también use HTTPS, previniendo que un atacante aproveche un subdominio no protegido para interceptar datos o realizar ataques MITM.

SECURE_HSTS_PRELOAD = True
# Protección contra: Conexiones inseguras en la primera visita y ataques MITM en navegadores que no han visitado tu sitio antes.
# Explicación: Al habilitar la precarga HSTS, tu dominio puede incluirse en una lista de precarga integrada en los navegadores modernos, asegurando que incluso en la primera visita, el navegador use HTTPS automáticamente. Esto elimina el riesgo de que un atacante intercepte la primera conexión antes de que el navegador reciba la política HSTS.

SESSION_COOKIE_SECURE = True
# Protección contra: Robo de cookies de sesión y ataques MITM.
# Explicación: Esta configuración asegura que las cookies de sesión solo se envíen a través de conexiones HTTPS, evitando que un atacante las intercepte en una conexión HTTP no cifrada. Esto es crucial para proteger las sesiones de usuario autenticadas, ya que un atacante con acceso a una cookie de sesión podría hacerse pasar por el usuario.

CSRF_COOKIE_SECURE = True
# Protección contra: Intercepción de tokens CSRF y ataques de falsificación de solicitudes entre sitios (CSRF) en conexiones no seguras.
# Explicación: Al garantizar que las cookies CSRF solo se envíen a través de HTTPS, esta configuración previene que un atacante intercepte el token CSRF en una conexión no cifrada. Esto refuerza la protección contra ataques CSRF, donde un atacante podría intentar enviar solicitudes maliciosas en nombre del usuario autenticado.
''' ----------------------------------------------------------------------------------------------------------------------------------------------------------- '''