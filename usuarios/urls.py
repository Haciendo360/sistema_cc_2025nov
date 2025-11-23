"""
URLs para la aplicación de usuarios

Este archivo contiene todas las rutas relacionadas con la gestión de usuarios:
- Autenticación (login, logout)
- Registro de usuarios
- Perfiles de usuario
- Gestión de usuarios (para administradores)
"""

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registro de usuarios
    path('registro/', views.registro_view, name='registro'),
    
    # Perfil de usuario
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    
    # Gestión de usuarios (solo administradores)
    path('gestion/', views.gestion_usuarios_view, name='gestion_usuarios'),
    path('gestion/aprobar/<int:usuario_id>/', views.aprobar_usuario_view, name='aprobar_usuario'),
    path('gestion/rechazar/<int:usuario_id>/', views.rechazar_usuario_view, name='rechazar_usuario'),
    path('gestion/eliminar/<int:usuario_id>/', views.eliminar_usuario_view, name='eliminar_usuario'),
    
    # Cambio de contraseña
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),
    
    # Recuperación de contraseña
    path('recuperar-password/', views.recuperar_password_view, name='recuperar_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
    
    # API endpoints para gestión de usuarios
    path('api/usuario/<int:usuario_id>/', views.api_obtener_usuario, name='api_obtener_usuario'),
    path('api/usuario/<int:usuario_id>/editar/', views.api_editar_usuario, name='api_editar_usuario'),
]
