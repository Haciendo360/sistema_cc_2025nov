"""
Configuración de URLs para el Sistema de Gestión de Casos Comunitarios - Jueces de Paz

Este archivo contiene todas las rutas principales del sistema:
- Panel de administración de Django
- URLs de usuarios (autenticación, registro, perfiles)
- URLs de casos (gestión de casos comunitarios)
- URLs de archivos media y estáticos
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Vista para redirigir la raíz al panel de administración
def redirect_to_admin(request):
    return redirect('/admin/')

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # Redirección de la raíz al panel de administración
    path('', redirect_to_admin, name='home'),
    
    # URLs de usuarios (autenticación, registro, perfiles)
    path('usuarios/', include('usuarios.urls')),
    
    # URLs de casos (gestión de casos comunitarios)
    path('casos/', include('casos.urls')),
    
    # URLs de API REST (si se implementa en el futuro)
    # path('api/', include('api.urls')),
]

# Configuración para servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Configuración para Django Debug Toolbar (solo en desarrollo)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
