"""
Vistas para la aplicación de usuarios

Este archivo contiene todas las vistas relacionadas con la gestión de usuarios:
- Autenticación (login, logout)
- Registro de usuarios con aprobación
- Perfiles de usuario
- Gestión de usuarios (para administradores)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
import uuid
import hashlib
from .models import Usuario, PerfilUsuario, Auditoria
from .forms import (
    LoginForm, RegistroForm, PerfilForm, 
    CambiarPasswordForm, RecuperarPasswordForm, ResetPasswordForm
)


def login_view(request):
    """
    Vista para el login de usuarios
    Solo permite acceso a usuarios aprobados
    """
    if request.user.is_authenticated:
        return redirect('casos:panel_juez' if request.user.es_juez() else 'casos:panel_admin')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.esta_aprobado() and user.is_active:
                    login(request, user)
                    
                    # Registrar en auditoría
                    Auditoria.registrar_accion(
                        usuario=user,
                        accion='login',
                        modelo_afectado='Usuario',
                        objeto_id=str(user.id),
                        descripcion=f'Usuario {user.username} inició sesión',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT')
                    )
                    
                    messages.success(request, f'¡Bienvenido, {user.get_full_name()}!')
                    
                    # Redirigir según el rol o al parámetro next
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    
                    if user.es_juez():
                        return redirect('casos:panel_juez')
                    elif user.es_admin():
                        return redirect('casos:panel_admin')
                else:
                    messages.error(request, 'Su cuenta está pendiente de aprobación o inactiva.')
            else:
                messages.error(request, 'Credenciales inválidas.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    """
    Vista para cerrar sesión
    """
    if request.user.is_authenticated:
        # Registrar en auditoría
        Auditoria.registrar_accion(
            usuario=request.user,
            accion='logout',
            modelo_afectado='Usuario',
            objeto_id=str(request.user.id),
            descripcion=f'Usuario {request.user.username} cerró sesión',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        logout(request)
        messages.info(request, 'Has cerrado sesión correctamente.')
    
    return redirect('usuarios:login')


def registro_view(request):
    """
    Vista para el registro de nuevos usuarios
    Los usuarios quedan en estado 'pendiente' hasta aprobación
    """
    if request.user.is_authenticated:
        return redirect('casos:panel_juez' if request.user.es_juez() else 'casos:panel_admin')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            # Crear usuario
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.estado_aprobacion = 'pendiente'
            user.save()
            
            # Crear perfil de usuario
            PerfilUsuario.objects.create(usuario=user)
            
            # Registrar en auditoría
            Auditoria.registrar_accion(
                usuario=user,
                accion='crear',
                modelo_afectado='Usuario',
                objeto_id=str(user.id),
                descripcion=f'Nuevo usuario registrado: {user.username}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, 'Registro exitoso. Su cuenta está pendiente de aprobación.')
            return redirect('usuarios:login')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def perfil_view(request):
    """
    Vista para ver el perfil del usuario actual
    """
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        perfil = PerfilUsuario.objects.create(usuario=request.user)
    
    return render(request, 'usuarios/perfil.html', {'perfil': perfil})


@login_required
def editar_perfil_view(request):
    """
    Vista para editar el perfil del usuario actual
    """
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        perfil = PerfilUsuario.objects.create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(instance=perfil)
    
    return render(request, 'usuarios/editar_perfil.html', {'form': form})


@login_required
def gestion_usuarios_view(request):
    """
    Vista para gestión de usuarios (solo administradores)
    """
    if not request.user.es_admin():
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('casos:panel_juez')
    
    # Filtrar usuarios según parámetros
    estado = request.GET.get('estado', '')
    rol = request.GET.get('rol', '')
    busqueda = request.GET.get('busqueda', '')
    
    usuarios = Usuario.objects.all()
    
    if estado:
        usuarios = usuarios.filter(estado_aprobacion=estado)
    
    if rol:
        usuarios = usuarios.filter(rol=rol)
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(username__icontains=busqueda) |
            Q(cedula__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'estado': estado,
        'rol': rol,
        'busqueda': busqueda,
        'usuarios_pendientes': Usuario.objects.filter(estado_aprobacion='pendiente').count(),
    }
    
    return render(request, 'usuarios/gestion_usuarios.html', context)


@login_required
def aprobar_usuario_view(request, usuario_id):
    """
    Vista para aprobar un usuario (solo administradores)
    """
    if not request.user.es_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('casos:panel_juez')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        observaciones = request.POST.get('observaciones', '')
        
        usuario.estado_aprobacion = 'aprobado'
        usuario.fecha_aprobacion = timezone.now()
        usuario.aprobado_por = request.user
        usuario.observaciones_aprobacion = observaciones
        usuario.save()
        
        messages.success(request, f'Usuario {usuario.get_full_name()} aprobado correctamente.')
        return redirect('usuarios:gestion_usuarios')
    
    return render(request, 'usuarios/aprobar_usuario.html', {'usuario': usuario})


@login_required
def rechazar_usuario_view(request, usuario_id):
    """
    Vista para rechazar un usuario (solo administradores)
    """
    if not request.user.es_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('casos:panel_juez')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        observaciones = request.POST.get('observaciones', '')
        
        usuario.estado_aprobacion = 'rechazado'
        usuario.fecha_aprobacion = timezone.now()
        usuario.aprobado_por = request.user
        usuario.observaciones_aprobacion = observaciones
        usuario.save()
        
        messages.success(request, f'Usuario {usuario.get_full_name()} rechazado.')
        return redirect('usuarios:gestion_usuarios')
    
    return render(request, 'usuarios/rechazar_usuario.html', {'usuario': usuario})


@login_required
def eliminar_usuario_view(request, usuario_id):
    """
    Vista para eliminar un usuario (solo administradores)
    """
    if not request.user.es_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('casos:panel_juez')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Evitar que el admin se elimine a sí mismo
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('usuarios:gestion_usuarios')
    
    if request.method == 'POST':
        nombre_usuario = usuario.get_full_name()
        
        # Registrar en auditoría antes de eliminar
        Auditoria.registrar_accion(
            usuario=request.user,
            accion='eliminar',
            modelo_afectado='Usuario',
            objeto_id=str(usuario.id),
            descripcion=f'Usuario eliminado: {usuario.username} ({nombre_usuario})',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        usuario.delete()
        messages.success(request, f'Usuario {nombre_usuario} eliminado correctamente.')
        return redirect('usuarios:gestion_usuarios')
    
    return redirect('usuarios:gestion_usuarios')



@login_required
def cambiar_password_view(request):
    """
    Vista para cambiar la contraseña del usuario actual
    """
    if request.method == 'POST':
        form = CambiarPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contraseña cambiada correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = CambiarPasswordForm(request.user)
    
    return render(request, 'usuarios/cambiar_password.html', {'form': form})


def recuperar_password_view(request):
    """
    Vista para solicitar recuperación de contraseña
    """
    if request.user.is_authenticated:
        return redirect('casos:panel_juez' if request.user.es_juez() else 'casos:panel_admin')
    
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Se ha enviado un enlace de recuperación a tu email.')
            return redirect('usuarios:login')
    else:
        form = RecuperarPasswordForm()
    
    return render(request, 'usuarios/recuperar_password.html', {'form': form})


def reset_password_view(request, token):
    """
    Vista para restablecer la contraseña con token
    """
    if request.user.is_authenticated:
        return redirect('casos:panel_juez' if request.user.es_juez() else 'casos:panel_admin')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Contraseña restablecida correctamente.')
            return redirect('usuarios:login')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'usuarios/reset_password.html', {'form': form, 'token': token})


# API endpoints para gestión de usuarios
@login_required
def api_obtener_usuario(request, usuario_id):
    """
    API endpoint para obtener datos de un usuario específico
    """
    if not request.user.es_admin():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        data = {
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'cedula': usuario.cedula,
            'telefono': usuario.telefono,
            'direccion': usuario.direccion,
            'rol': usuario.rol,
            'estado_aprobacion': usuario.estado_aprobacion,
            'is_active': usuario.is_active,
            'is_staff': usuario.is_staff,
            'observaciones_aprobacion': usuario.observaciones_aprobacion,
        }
        return JsonResponse(data)
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)


@login_required
def api_editar_usuario(request, usuario_id):
    """
    API endpoint para editar un usuario
    """
    if not request.user.es_admin():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        
        # Actualizar campos
        usuario.email = request.POST.get('email', usuario.email)
        usuario.first_name = request.POST.get('first_name', usuario.first_name)
        usuario.last_name = request.POST.get('last_name', usuario.last_name)
        usuario.cedula = request.POST.get('cedula', usuario.cedula)
        usuario.telefono = request.POST.get('telefono', usuario.telefono)
        usuario.direccion = request.POST.get('direccion', usuario.direccion)
        usuario.rol = request.POST.get('rol', usuario.rol)
        usuario.estado_aprobacion = request.POST.get('estado_aprobacion', usuario.estado_aprobacion)
        usuario.is_active = request.POST.get('is_active') == 'on'
        usuario.is_staff = request.POST.get('is_staff') == 'on'
        usuario.observaciones_aprobacion = request.POST.get('observaciones_aprobacion', usuario.observaciones_aprobacion)
        
        # Si se cambió el estado de aprobación, registrar quién lo hizo
        if usuario.estado_aprobacion in ['aprobado', 'rechazado'] and not usuario.fecha_aprobacion:
            usuario.fecha_aprobacion = timezone.now()
            usuario.aprobado_por = request.user
        
        usuario.save()
        
        return JsonResponse({'success': True, 'message': 'Usuario actualizado correctamente'})
        
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
