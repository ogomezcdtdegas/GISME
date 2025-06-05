from .base import *
import os

DEBUG = False
#ALLOWED_HOSTS = ['tudominio.com']
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

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')