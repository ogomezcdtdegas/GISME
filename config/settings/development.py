from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS_DEV', '127.0.0.1,localhost,tudominio.com').split(',')
SESSION_COOKIE_AGE = 1200

<<<<<<< HEAD
=======

>>>>>>> msalonlyv43
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
<<<<<<< HEAD

=======
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''
>>>>>>> msalonlyv43
# Habilitar Swagger/Schema solo en desarrollo
REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'