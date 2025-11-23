"""
Configuración del Sistema de Gestión de Casos Comunitarios - Jueces de Paz
Desarrollado con Django 4.2.7

Este archivo contiene todas las configuraciones necesarias para el funcionamiento
del sistema de gestión de casos comunitarios, incluyendo:
- Configuración de base de datos
- Configuración de archivos estáticos y media
- Configuración de seguridad
- Configuración de aplicaciones instaladas
- Configuración de autenticación personalizada
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de seguridad
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-0^%sqcg8+niqm5m40$e=-n##-o8qj*4ja5h*vmn7al_hpe(eym')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Configuración de hosts permitidos para producción
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Configuración de CSRF para producción
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])


# Application definition
# Configuración de aplicaciones instaladas para el sistema de casos comunitarios

INSTALLED_APPS = [
    # Aplicaciones de Django por defecto
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Aplicaciones de terceros
    'rest_framework',
    'corsheaders',
    
    # Aplicaciones del proyecto
    'usuarios',  # Gestión de usuarios y autenticación
    'casos',     # Gestión de casos comunitarios
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS para API
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Servir archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sistema_casos_comunitario.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Directorio de templates personalizados
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # Para archivos media
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_casos_comunitario.wsgi.application'


# Database
# Configuración de base de datos para desarrollo y producción
# En desarrollo usa SQLite, en producción PostgreSQL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configuración para producción con PostgreSQL (Render.com)
if config('DATABASE_URL', default=''):
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(config('DATABASE_URL'))


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# Configuración de idioma y zona horaria para Ecuador

LANGUAGE_CODE = 'es-ec'  # Español Ecuador
TIME_ZONE = 'America/Guayaquil'  # Zona horaria de Ecuador
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# Configuración de archivos estáticos y media

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configuración de archivos media (adjuntos de casos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración de archivos estáticos con WhiteNoise para producción
# Usar CompressedManifestStaticFilesStorage con manifest_strict=False
# para evitar errores cuando faltan archivos en el manifest
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Configuración adicional para WhiteNoise
WHITENOISE_MANIFEST_STRICT = False  # No fallar si faltan archivos en el manifest

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de autenticación personalizada
# Usar nuestro modelo de usuario personalizado
AUTH_USER_MODEL = 'usuarios.Usuario'
LOGIN_URL = '/usuarios/login/'
LOGIN_REDIRECT_URL = '/casos/panel-juez/'
LOGOUT_REDIRECT_URL = '/usuarios/login/'

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Configuración de CORS para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Configuración de archivos adjuntos
# Límites para archivos adjuntos de casos
MAX_FILE_SIZE = config('MAX_FILE_SIZE', default=10485760, cast=int)  # 10MB
ALLOWED_FILE_TYPES = config('ALLOWED_FILE_TYPES', default='pdf,doc,docx,jpg,jpeg,png', cast=lambda v: [s.strip() for s in v.split(',')])

# Configuración de plazos legales
PLAZO_ESTANDAR_DIAS = config('PLAZO_ESTANDAR_DIAS', default=15, cast=int)
PLAZO_PRORROGA_DIAS = config('PLAZO_PRORROGA_DIAS', default=15, cast=int)
DIAS_ALERTA_URGENTE = config('DIAS_ALERTA_URGENTE', default=10, cast=int)

# Configuración de email para recuperación de contraseñas
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'casos': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'usuarios': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Configuración de seguridad adicional
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuración de sesiones
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
