"""
Modelos de datos para el Sistema de Gestión de Casos Comunitarios - Jueces de Paz

Este archivo contiene todos los modelos necesarios para el funcionamiento del sistema:
- Usuario: Modelo personalizado de usuario con roles y aprobación
- PerfilUsuario: Información adicional del usuario
- Auditoria: Registro de todas las acciones del sistema
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    Incluye roles específicos del sistema y sistema de aprobación
    """
    
    # Opciones para roles de usuario
    ROL_CHOICES = [
        ('juez', 'Juez de Paz'),
        ('admin', 'Administrador'),
    ]
    
    # Opciones para estado de aprobación
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    # Campos adicionales al modelo base de Django
    rol = models.CharField(
        max_length=10,
        choices=ROL_CHOICES,
        default='juez',
        verbose_name='Rol del Usuario',
        help_text='Rol que desempeña el usuario en el sistema'
    )
    
    estado_aprobacion = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado de Aprobación',
        help_text='Estado actual de aprobación del usuario'
    )
    
    cedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message='La cédula debe tener exactamente 10 dígitos'
        )],
        verbose_name='Cédula de Identidad',
        help_text='Cédula de identidad del usuario'
    )
    
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[\d\s\-\+\(\)]+$',
            message='Formato de teléfono inválido'
        )],
        verbose_name='Teléfono',
        help_text='Número de teléfono de contacto'
    )
    
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección',
        help_text='Dirección de residencia del usuario'
    )
    
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Registro',
        help_text='Fecha y hora en que se registró el usuario'
    )
    
    fecha_aprobacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Aprobación',
        help_text='Fecha y hora en que fue aprobado el usuario'
    )
    
    aprobado_por = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='usuarios_aprobados',
        verbose_name='Aprobado por',
        help_text='Usuario administrador que aprobó el registro'
    )
    
    observaciones_aprobacion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones de Aprobación',
        help_text='Observaciones del administrador al aprobar o rechazar'
    )
    
    # Configuración del modelo
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.get_rol_display()}"
    
    def get_rol_display(self):
        """Retorna el nombre legible del rol"""
        return dict(self.ROL_CHOICES).get(self.rol, self.rol)
    
    def get_estado_display(self):
        """Retorna el nombre legible del estado"""
        return dict(self.ESTADO_CHOICES).get(self.estado_aprobacion, self.estado_aprobacion)
    
    def es_juez(self):
        """Verifica si el usuario es un Juez de Paz"""
        return self.rol == 'juez' and self.estado_aprobacion == 'aprobado'
    
    def es_admin(self):
        """Verifica si el usuario es un Administrador"""
        return self.rol == 'admin' and self.estado_aprobacion == 'aprobado'
    
    def esta_aprobado(self):
        """Verifica si el usuario está aprobado"""
        return self.estado_aprobacion == 'aprobado'
    
    def puede_acceder_sistema(self):
        """Verifica si el usuario puede acceder al sistema"""
        return self.esta_aprobado() and self.is_active


class PerfilUsuario(models.Model):
    """
    Modelo para información adicional del perfil de usuario
    Incluye configuración personalizada y preferencias
    """
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar',
        help_text='Foto de perfil del usuario'
    )
    
    biografia = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        verbose_name='Biografía',
        help_text='Breve descripción personal del usuario'
    )
    
    especialidad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Especialidad',
        help_text='Especialidad o área de conocimiento del juez'
    )
    
    años_experiencia = models.PositiveIntegerField(
        default=0,
        verbose_name='Años de Experiencia',
        help_text='Años de experiencia como juez de paz'
    )
    
    # Configuración de notificaciones
    recibir_notificaciones_email = models.BooleanField(
        default=True,
        verbose_name='Recibir Notificaciones por Email',
        help_text='Si desea recibir notificaciones por correo electrónico'
    )
    
    recibir_alertas_casos = models.BooleanField(
        default=True,
        verbose_name='Recibir Alertas de Casos',
        help_text='Si desea recibir alertas sobre casos urgentes'
    )
    
    # Configuración de interfaz
    tema_preferido = models.CharField(
        max_length=20,
        choices=[
            ('claro', 'Tema Claro'),
            ('oscuro', 'Tema Oscuro'),
            ('auto', 'Automático'),
        ],
        default='claro',
        verbose_name='Tema Preferido',
        help_text='Tema de interfaz preferido'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización',
        help_text='Última vez que se actualizó el perfil'
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name()}"


class Auditoria(models.Model):
    """
    Modelo para registrar todas las acciones del sistema
    Proporciona trazabilidad completa de las operaciones
    """
    
    # Tipos de acciones que se pueden registrar
    ACCION_CHOICES = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('aprobar', 'Aprobar'),
        ('rechazar', 'Rechazar'),
        ('login', 'Iniciar Sesión'),
        ('logout', 'Cerrar Sesión'),
        ('cambiar_password', 'Cambiar Contraseña'),
        ('subir_archivo', 'Subir Archivo'),
        ('descargar_archivo', 'Descargar Archivo'),
    ]
    
    # Campos principales del registro de auditoría
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID de Auditoría'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario',
        help_text='Usuario que realizó la acción'
    )
    
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        verbose_name='Acción Realizada',
        help_text='Tipo de acción que se registró'
    )
    
    modelo_afectado = models.CharField(
        max_length=50,
        verbose_name='Modelo Afectado',
        help_text='Nombre del modelo que fue afectado'
    )
    
    objeto_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='ID del Objeto',
        help_text='ID del objeto específico que fue afectado'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción detallada de la acción realizada'
    )
    
    datos_anteriores = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Datos Anteriores',
        help_text='Estado anterior del objeto (para ediciones)'
    )
    
    datos_nuevos = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Datos Nuevos',
        help_text='Estado nuevo del objeto (para ediciones)'
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Dirección IP',
        help_text='Dirección IP desde donde se realizó la acción'
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='User Agent',
        help_text='Información del navegador utilizado'
    )
    
    fecha_accion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Acción',
        help_text='Fecha y hora en que se realizó la acción'
    )
    
    # Configuración del modelo
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-fecha_accion']
        indexes = [
            models.Index(fields=['usuario', 'fecha_accion']),
            models.Index(fields=['modelo_afectado', 'objeto_id']),
            models.Index(fields=['accion', 'fecha_accion']),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.modelo_afectado} - {self.fecha_accion.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def registrar_accion(cls, usuario, accion, modelo_afectado, descripcion, 
                        objeto_id=None, datos_anteriores=None, datos_nuevos=None,
                        ip_address=None, user_agent=None):
        """
        Método de clase para registrar una acción de auditoría
        Simplifica el proceso de registro de auditoría
        """
        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            modelo_afectado=modelo_afectado,
            objeto_id=objeto_id,
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=ip_address,
            user_agent=user_agent
        )