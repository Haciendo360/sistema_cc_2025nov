"""
Configuración del panel de administración de Django
para la gestión de casos comunitarios
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Caso, Adjunto, Observacion, ConfiguracionSistema


@admin.register(Caso)
class CasoAdmin(admin.ModelAdmin):
    """
    Administración personalizada del modelo Caso
    """
    list_display = (
        'numero_caso', 'nombre_solicitante', 'juez_asignado', 
        'tipo_conflicto', 'estado', 'fecha_registro', 'progreso_bar'
    )
    list_filter = (
        'estado', 'tipo_conflicto', 'bloque_residencial', 
        'juez_asignado', 'fecha_registro', 'prorroga_solicitada'
    )
    search_fields = (
        'numero_caso', 'nombre_solicitante', 'cedula_solicitante',
        'nombre_involucrado', 'cedula_involucrado', 'descripcion_caso'
    )
    ordering = ('-fecha_registro',)
    readonly_fields = (
        'numero_caso', 'fecha_registro', 'fecha_limite', 
        'fecha_actualizacion', 'progreso_bar', 'estado_urgente'
    )
    
    fieldsets = (
        ('Información del Caso', {
            'fields': (
                'numero_caso', 'juez_asignado', 'tipo_conflicto', 
                'bloque_residencial', 'estado', 'descripcion_caso'
            )
        }),
        ('Información del Solicitante', {
            'fields': (
                'cedula_solicitante', 'nombre_solicitante', 
                'telefono_solicitante', 'direccion_solicitante'
            )
        }),
        ('Información del Involucrado', {
            'fields': (
                'cedula_involucrado', 'nombre_involucrado', 
                'telefono_involucrado', 'direccion_involucrado'
            ),
            'classes': ('collapse',)
        }),
        ('Fechas y Plazos', {
            'fields': (
                'fecha_registro', 'fecha_limite', 'fecha_prorroga',
                'fecha_resolucion', 'fecha_cierre'
            ),
            'classes': ('collapse',)
        }),
        ('Control de Prórroga', {
            'fields': (
                'prorroga_solicitada', 'justificacion_prorroga', 
                'fecha_solicitud_prorroga'
            ),
            'classes': ('collapse',)
        }),
        ('Resolución del Caso', {
            'fields': (
                'medio_resolucion', 'observaciones_resolucion'
            ),
            'classes': ('collapse',)
        }),
        ('Seguimiento', {
            'fields': (
                'progreso_bar', 'estado_urgente', 'creado_por', 
                'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def progreso_bar(self, obj):
        """Mostrar barra de progreso visual"""
        progreso = obj.calcular_progreso()
        estado_urgente = obj.obtener_estado_urgente()
        
        color = 'bg-success'
        if estado_urgente == 'urgente':
            color = 'bg-warning'
        elif estado_urgente == 'vencido':
            color = 'bg-danger'
        
        return format_html(
            '<div class="progress" style="width: 200px;">'
            '<div class="progress-bar {}" role="progressbar" '
            'style="width: {}%" aria-valuenow="{}" '
            'aria-valuemin="0" aria-valuemax="100">'
            '{}%</div></div>',
            color, progreso, progreso, round(progreso)
        )
    progreso_bar.short_description = 'Progreso'
    
    def estado_urgente(self, obj):
        """Mostrar estado urgente con colores"""
        estado = obj.obtener_estado_urgente()
        
        if estado == 'normal':
            return format_html('<span class="badge bg-success">En Tiempo</span>')
        elif estado == 'urgente':
            return format_html('<span class="badge bg-warning">Urgente</span>')
        elif estado == 'vencido':
            return format_html('<span class="badge bg-danger">Vencido</span>')
        
        return estado
    estado_urgente.short_description = 'Estado Urgente'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'juez_asignado', 'creado_por'
        )


@admin.register(Adjunto)
class AdjuntoAdmin(admin.ModelAdmin):
    """
    Administración del modelo Adjunto
    """
    list_display = (
        'nombre_archivo', 'caso', 'tipo_archivo', 
        'tamaño_formateado', 'subido_por', 'fecha_subida'
    )
    list_filter = ('tipo_archivo', 'es_publico', 'fecha_subida', 'subido_por')
    search_fields = ('nombre_archivo', 'caso__numero_caso', 'descripcion')
    readonly_fields = ('tamaño_archivo', 'fecha_subida')
    ordering = ('-fecha_subida',)
    
    fieldsets = (
        ('Información del Archivo', {
            'fields': ('caso', 'nombre_archivo', 'archivo', 'tipo_archivo')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'tamaño_archivo', 'es_publico')
        }),
        ('Metadatos', {
            'fields': ('subido_por', 'fecha_subida'),
            'classes': ('collapse',)
        }),
    )
    
    def tamaño_formateado(self, obj):
        """Mostrar tamaño formateado"""
        return obj.obtener_tamaño_formateado()
    tamaño_formateado.short_description = 'Tamaño'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'caso', 'subido_por'
        )


@admin.register(Observacion)
class ObservacionAdmin(admin.ModelAdmin):
    """
    Administración del modelo Observacion
    """
    list_display = (
        'caso', 'usuario', 'contenido_preview', 
        'es_interna', 'fecha_creacion'
    )
    list_filter = ('es_interna', 'fecha_creacion', 'usuario')
    search_fields = ('caso__numero_caso', 'contenido', 'usuario__username')
    readonly_fields = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('caso', 'usuario', 'contenido')
        }),
        ('Configuración', {
            'fields': ('es_interna', 'fecha_creacion')
        }),
    )
    
    def contenido_preview(self, obj):
        """Mostrar preview del contenido"""
        preview = obj.contenido[:50]
        if len(obj.contenido) > 50:
            preview += '...'
        return preview
    contenido_preview.short_description = 'Contenido'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'caso', 'usuario'
        )


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    """
    Administración del modelo ConfiguracionSistema
    """
    list_display = (
        'nombre_sistema', 'plazo_estandar_dias', 
        'plazo_prorroga_dias', 'fecha_actualizacion'
    )
    readonly_fields = ('fecha_actualizacion',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre_sistema', 'logo_sistema')
        }),
        ('Personalización Visual', {
            'fields': ('color_primario', 'color_secundario', 'texto_pie_pagina')
        }),
        ('Configuración de Plazos', {
            'fields': (
                'plazo_estandar_dias', 'plazo_prorroga_dias', 
                'dias_alerta_urgente'
            )
        }),
        ('Configuración de Archivos', {
            'fields': (
                'tamaño_maximo_archivo_mb', 'tipos_archivo_permitidos'
            )
        }),
        ('Metadatos', {
            'fields': ('fecha_actualizacion',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Solo permitir una configuración del sistema"""
        return not ConfiguracionSistema.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar la configuración del sistema"""
        return False


# Configuración adicional del sitio de administración
admin.site.site_header = "Sistema de Gestión de Casos Comunitarios - Jueces de Paz"
admin.site.site_title = "Administración del Sistema"
admin.site.index_title = "Panel de Administración"