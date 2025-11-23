"""
Script para crear superusuario automáticamente en Render
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_casos_comunitario.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Obtener credenciales de variables de entorno
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin123!')

# Crear superusuario si no existe
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        rol='admin',
        estado_aprobacion='aprobado'
    )
    print(f'✅ Superusuario "{username}" creado exitosamente')
else:
    print(f'ℹ️  Superusuario "{username}" ya existe')
