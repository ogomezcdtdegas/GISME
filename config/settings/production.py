from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS_PROD', 'tudominio.com').split(',')
SESSION_COOKIE_AGE = 1800

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

# Configuraciones de seguridad adicionales para Azure
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')