"""
Configuración del panel de administración de Django
para el Sistema de Gestión de Casos Comunitarios
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone

from .models import Usuario, PerfilUsuario, Auditoria


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Administración personalizada del modelo Usuario
    """
    list_display = ('username', 'get_full_name', 'cedula', 'rol', 'estado_aprobacion', 'is_active', 'fecha_registro', 'acciones_rapidas')
    list_filter = ('rol', 'estado_aprobacion', 'is_active', 'is_staff', 'fecha_registro')
    search_fields = ('username', 'first_name', 'last_name', 'cedula', 'email')
    ordering = ('-fecha_registro',)
    
    # Campos que se muestran al agregar un usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'cedula', 'telefono', 'direccion', 'rol', 'estado_aprobacion'),
        }),
    )
    
    # Campos que se muestran al editar un usuario
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'cedula', 'telefono', 'direccion')
        }),
        ('Configuración del Sistema', {
            'fields': ('rol', 'estado_aprobacion', 'aprobado_por', 'observaciones_aprobacion')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'fecha_registro', 'fecha_aprobacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_registro', 'fecha_aprobacion', 'date_joined', 'last_login')
    
    def get_full_name(self, obj):
        """Mostrar nombre completo en la lista"""
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Nombre Completo'
    
    def acciones_rapidas(self, obj):
        """Mostrar botones de acción rápida"""
        if obj.estado_aprobacion == 'pendiente':
            return format_html(
                '<a href="/usuarios/aprobar/{}/" class="btn btn-success btn-sm" title="Aprobar">'
                '<i class="fas fa-check"></i></a> '
                '<a href="/usuarios/rechazar/{}/" class="btn btn-danger btn-sm" title="Rechazar">'
                '<i class="fas fa-times"></i></a>',
                obj.id, obj.id
            )
        elif obj.estado_aprobacion == 'aprobado':
            return format_html(
                '<span class="badge badge-success">Aprobado</span>'
            )
        else:
            return format_html(
                '<span class="badge badge-danger">Rechazado</span>'
            )
    acciones_rapidas.short_description = 'Acciones'
    acciones_rapidas.allow_tags = True
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related('aprobado_por')
    
    def save_model(self, request, obj, form, change):
        """Personalizar el guardado del modelo"""
        if not change:  # Si es un nuevo usuario
            obj.fecha_registro = timezone.now()
            if not obj.estado_aprobacion:
                obj.estado_aprobacion = 'pendiente'
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        """Agregar URLs personalizadas"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('aprobar/<int:usuario_id>/', self.admin_site.admin_view(self.aprobar_usuario), name='aprobar_usuario'),
            path('rechazar/<int:usuario_id>/', self.admin_site.admin_view(self.rechazar_usuario), name='rechazar_usuario'),
        ]
        return custom_urls + urls
    
    def aprobar_usuario(self, request, usuario_id):
        """Vista para aprobar usuario desde el admin"""
        from django.shortcuts import redirect
        from django.contrib import messages
        
        usuario = self.get_object(request, usuario_id)
        if usuario:
            usuario.estado_aprobacion = 'aprobado'
            usuario.fecha_aprobacion = timezone.now()
            usuario.aprobado_por = request.user
            usuario.save()
            messages.success(request, f'Usuario {usuario.username} aprobado correctamente.')
        
        return redirect('admin:usuarios_usuario_changelist')
    
    def rechazar_usuario(self, request, usuario_id):
        """Vista para rechazar usuario desde el admin"""
        from django.shortcuts import redirect
        from django.contrib import messages
        
        usuario = self.get_object(request, usuario_id)
        if usuario:
            usuario.estado_aprobacion = 'rechazado'
            usuario.fecha_aprobacion = timezone.now()
            usuario.aprobado_por = request.user
            usuario.save()
            messages.success(request, f'Usuario {usuario.username} rechazado.')
        
        return redirect('admin:usuarios_usuario_changelist')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """
    Administración del modelo PerfilUsuario
    """
    list_display = ('usuario', 'especialidad', 'años_experiencia', 'fecha_actualizacion')
    list_filter = ('especialidad', 'recibir_notificaciones_email', 'recibir_alertas_casos', 'tema_preferido')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'especialidad')
    readonly_fields = ('fecha_actualizacion',)
    
    fieldsets = (
        ('Usuario', {'fields': ('usuario',)}),
        ('Información Profesional', {
            'fields': ('especialidad', 'años_experiencia', 'biografia')
        }),
        ('Configuración de Notificaciones', {
            'fields': ('recibir_notificaciones_email', 'recibir_alertas_casos')
        }),
        ('Configuración de Interfaz', {
            'fields': ('tema_preferido', 'avatar')
        }),
        ('Fechas', {
            'fields': ('fecha_actualizacion',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    """
    Administración del modelo Auditoria
    """
    list_display = ('fecha_accion', 'usuario', 'accion', 'modelo_afectado', 'objeto_id', 'ip_address')
    list_filter = ('accion', 'modelo_afectado', 'fecha_accion', 'usuario')
    search_fields = ('usuario__username', 'descripcion', 'objeto_id', 'ip_address')
    readonly_fields = ('id', 'fecha_accion', 'ip_address', 'user_agent')
    ordering = ('-fecha_accion',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('id', 'usuario', 'accion', 'fecha_accion')
        }),
        ('Detalles de la Acción', {
            'fields': ('modelo_afectado', 'objeto_id', 'descripcion')
        }),
        ('Datos del Objeto', {
            'fields': ('datos_anteriores', 'datos_nuevos'),
            'classes': ('collapse',)
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """No permitir agregar registros de auditoría manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir modificar registros de auditoría"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar registros de auditoría"""
        return request.user.is_superuser


# Configuración del sitio de administración
admin.site.site_header = "Sistema de Gestión de Casos Comunitarios - Jueces de Paz"
admin.site.site_title = "Administración del Sistema"
admin.site.index_title = "Panel de Administración"