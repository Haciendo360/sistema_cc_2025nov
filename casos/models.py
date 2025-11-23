"""
Modelos de datos para la gestión de casos comunitarios

Este archivo contiene todos los modelos necesarios para el manejo de casos:
- Caso: Modelo principal para casos comunitarios
- Adjunto: Archivos adjuntos a los casos
- Observacion: Observaciones y notas del caso
- ConfiguracionSistema: Configuración general del sistema
"""

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, FileExtensionValidator
from django.conf import settings
from usuarios.models import Usuario, Auditoria
import uuid
import os


def generar_numero_caso():
    """
    Genera un número de caso único con formato JC-AÑO-MES-XXXX
    Ejemplo: JC-2024-01-0001
    """
    año = timezone.now().year
    mes = timezone.now().month
    mes_str = f"{mes:02d}"
    
    # Buscar el último caso del mes actual
    ultimo_caso = Caso.objects.filter(
        numero_caso__startswith=f"JC-{año}-{mes_str}-"
    ).order_by('-numero_caso').first()
    
    if ultimo_caso:
        # Extraer el número secuencial del último caso
        try:
            ultimo_numero = int(ultimo_caso.numero_caso.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        except (ValueError, IndexError):
            nuevo_numero = 1
    else:
        nuevo_numero = 1
    
    return f"JC-{año}-{mes_str}-{nuevo_numero:04d}"


def upload_to_adjuntos(instance, filename):
    """
    Función para determinar la ruta de subida de archivos adjuntos
    Organiza los archivos por año/mes/caso
    """
    año = timezone.now().year
    mes = timezone.now().month
    return f'adjuntos/{año}/{mes:02d}/{instance.caso.numero_caso}/{filename}'


class Caso(models.Model):
    """
    Modelo principal para casos comunitarios
    Contiene toda la información del caso y su seguimiento
    """
    
    # Opciones para tipos de conflicto - Ley Orgánica de Justicia de Paz Comunal de Venezuela
    TIPO_CONFLICTO_CHOICES = [
        ('vecinal', 'Vecinal'),
        ('individual', 'Individual'),
        ('comunitario', 'Comunitario'),
        ('contravencion', 'Contravención sin Privación de Libertad'),
        ('obligacion_patrimonial', 'Obligación Patrimonial (hasta 5 salarios básicos)'),
        ('otro', 'Otro'),
    ]
    
    # Opciones para estados del caso
    ESTADO_CHOICES = [
        ('en_tramite', 'En Trámite'),
        ('resuelto', 'Resuelto'),
        ('no_resuelto', 'No Resuelto'),
        ('archivado', 'Archivado'),
    ]
    
    # Opciones para medios de resolución
    MEDIO_RESOLUCION_CHOICES = [
        ('conciliacion', 'Conciliación'),
        ('mediacion', 'Mediación'),
        ('arbitraje', 'Arbitraje'),
        ('sentencia', 'Sentencia'),
        ('desistimiento', 'Desistimiento'),
        ('otro', 'Otro'),
    ]
    
    # Campos principales del caso
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID del Caso'
    )
    
    numero_caso = models.CharField(
        max_length=20,
        unique=True,
        default=generar_numero_caso,
        verbose_name='Número de Caso',
        help_text='Número único del caso generado automáticamente'
    )
    
    juez_asignado = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='casos_asignados',
        verbose_name='Juez Asignado',
        help_text='Juez de Paz responsable del caso'
    )
    
    # Información del solicitante
    cedula_solicitante = models.CharField(
        max_length=10,
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message='La cédula debe tener exactamente 10 dígitos'
        )],
        verbose_name='Cédula del Solicitante',
        help_text='Cédula de identidad de quien presenta el caso'
    )
    
    nombre_solicitante = models.CharField(
        max_length=100,
        verbose_name='Nombre del Solicitante',
        help_text='Nombre completo del solicitante'
    )
    
    telefono_solicitante = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Teléfono del Solicitante',
        help_text='Número de teléfono del solicitante'
    )
    
    direccion_solicitante = models.TextField(
        verbose_name='Dirección del Solicitante',
        help_text='Dirección de residencia del solicitante'
    )
    
    # Información del involucrado
    cedula_involucrado = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message='La cédula debe tener exactamente 10 dígitos'
        )],
        verbose_name='Cédula del Involucrado',
        help_text='Cédula de identidad de la persona involucrada'
    )
    
    nombre_involucrado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nombre del Involucrado',
        help_text='Nombre completo de la persona involucrada'
    )
    
    telefono_involucrado = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Teléfono del Involucrado',
        help_text='Número de teléfono del involucrado'
    )
    
    direccion_involucrado = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección del Involucrado',
        help_text='Dirección de residencia del involucrado'
    )
    
    # Información del caso
    tipo_conflicto = models.CharField(
        max_length=30,
        choices=TIPO_CONFLICTO_CHOICES,
        verbose_name='Tipo de Conflicto',
        help_text='Tipo de conflicto que se presenta'
    )
    
    descripcion_caso = models.TextField(
        verbose_name='Descripción del Caso',
        help_text='Descripción detallada del conflicto presentado'
    )
    
    bloque_residencial = models.CharField(
        max_length=10,
        choices=[
            ('BLOQUE_15', 'Bloque 15'),
            ('BLOQUE_16', 'Bloque 16'),
            ('BLOQUE_17', 'Bloque 17'),
            ('BLOQUE_18', 'Bloque 18'),
            ('BLOQUE_19', 'Bloque 19'),
            ('BLOQUE_20', 'Bloque 20'),
            ('BLOQUE_21', 'Bloque 21'),
            ('BLOQUE_22P', 'Bloque 22P'),
            ('BLOQUE_23P', 'Bloque 23P'),
            ('BLOQUE_24P', 'Bloque 24P'),
            ('BLOQUE_25P', 'Bloque 25P'),
        ],
        verbose_name='Bloque Residencial',
        help_text='Bloque residencial donde ocurre el conflicto'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='en_tramite',
        verbose_name='Estado del Caso',
        help_text='Estado actual del caso'
    )
    
    # Fechas importantes
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Registro',
        help_text='Fecha y hora en que se registró el caso'
    )
    
    fecha_limite = models.DateTimeField(
        verbose_name='Fecha Límite',
        help_text='Fecha límite para resolver el caso (15 días)'
    )
    
    fecha_prorroga = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Prórroga',
        help_text='Fecha límite con prórroga (+15 días adicionales)'
    )
    
    fecha_resolucion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Resolución',
        help_text='Fecha en que se resolvió el caso'
    )
    
    fecha_cierre = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Cierre',
        help_text='Fecha en que se cerró definitivamente el caso'
    )
    
    # Información de resolución
    medio_resolucion = models.CharField(
        max_length=20,
        choices=MEDIO_RESOLUCION_CHOICES,
        blank=True,
        null=True,
        verbose_name='Medio de Resolución',
        help_text='Medio utilizado para resolver el caso'
    )
    
    observaciones_resolucion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones de Resolución',
        help_text='Observaciones sobre la resolución del caso'
    )
    
    # Control de prórroga
    prorroga_solicitada = models.BooleanField(
        default=False,
        verbose_name='Prórroga Solicitada',
        help_text='Indica si se ha solicitado prórroga para este caso'
    )
    
    justificacion_prorroga = models.TextField(
        blank=True,
        null=True,
        verbose_name='Justificación de Prórroga',
        help_text='Justificación para solicitar la prórroga'
    )
    
    fecha_solicitud_prorroga = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Solicitud de Prórroga',
        help_text='Fecha en que se solicitó la prórroga'
    )
    
    # Campos de auditoría
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='casos_creados',
        verbose_name='Creado por',
        help_text='Usuario que creó el caso'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización',
        help_text='Última vez que se actualizó el caso'
    )
    
    class Meta:
        verbose_name = 'Caso Comunitario'
        verbose_name_plural = 'Casos Comunitarios'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['numero_caso']),
            models.Index(fields=['juez_asignado', 'estado']),
            models.Index(fields=['cedula_solicitante']),
            models.Index(fields=['fecha_registro']),
            models.Index(fields=['estado', 'fecha_limite']),
        ]
    
    def __str__(self):
        return f"{self.numero_caso} - {self.nombre_solicitante}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para calcular fechas límite automáticamente
        """
        if not self.pk:  # Solo para casos nuevos
            # Establecer fecha de registro si no está establecida
            if not self.fecha_registro:
                self.fecha_registro = timezone.now()
            
            # Calcular fecha límite (15 días desde el registro)
            self.fecha_limite = self.fecha_registro + timezone.timedelta(
                days=settings.PLAZO_ESTANDAR_DIAS
            )
        
        super().save(*args, **kwargs)
    
    def calcular_progreso(self):
        """
        Calcula el progreso del caso basado en los días transcurridos
        Retorna un porcentaje de 0 a 100
        """
        ahora = timezone.now()
        
        if self.estado in ['resuelto', 'no_resuelto', 'archivado']:
            return 100
        
        # Usar fecha de prórroga si existe, sino fecha límite
        fecha_final = self.fecha_prorroga if self.fecha_prorroga else self.fecha_limite
        
        dias_totales = settings.PLAZO_ESTANDAR_DIAS
        if self.fecha_prorroga:
            dias_totales += settings.PLAZO_PRORROGA_DIAS
        
        dias_transcurridos = (ahora - self.fecha_registro).days
        
        progreso = min((dias_transcurridos / dias_totales) * 100, 100)
        return max(progreso, 0)
    
    def obtener_estado_urgente(self):
        """
        Determina si el caso está en estado urgente o vencido
        Retorna: 'normal', 'urgente', 'vencido'
        """
        ahora = timezone.now()
        fecha_final = self.fecha_prorroga if self.fecha_prorroga else self.fecha_limite
        
        if self.estado in ['resuelto', 'no_resuelto', 'archivado']:
            return 'normal'
        
        dias_restantes = (fecha_final - ahora).days
        
        if dias_restantes < 0:
            return 'vencido'
        elif dias_restantes <= settings.DIAS_ALERTA_URGENTE:
            return 'urgente'
        else:
            return 'normal'
    
    def puede_solicitar_prorroga(self):
        """
        Verifica si el caso puede solicitar prórroga
        Solo se permite una prórroga por caso
        """
        return not self.prorroga_solicitada and self.estado == 'en_tramite'
    
    def solicitar_prorroga(self, justificacion, usuario):
        """
        Solicita prórroga para el caso
        """
        if self.puede_solicitar_prorroga():
            self.prorroga_solicitada = True
            self.justificacion_prorroga = justificacion
            self.fecha_solicitud_prorroga = timezone.now()
            self.fecha_prorroga = self.fecha_limite + timezone.timedelta(
                days=settings.PLAZO_PRORROGA_DIAS
            )
            self.save()
            
            # Registrar en auditoría
            Auditoria.registrar_accion(
                usuario=usuario,
                accion='editar',
                modelo_afectado='Caso',
                objeto_id=str(self.id),
                descripcion=f'Solicitud de prórroga para caso {self.numero_caso}',
                datos_nuevos={'prorroga_solicitada': True, 'justificacion': justificacion}
            )
            
            return True
        return False


class Adjunto(models.Model):
    """
    Modelo para archivos adjuntos a los casos
    Permite subir documentos relacionados con cada caso
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID del Adjunto'
    )
    
    caso = models.ForeignKey(
        Caso,
        on_delete=models.CASCADE,
        related_name='adjuntos',
        verbose_name='Caso',
        help_text='Caso al que pertenece el adjunto'
    )
    
    nombre_archivo = models.CharField(
        max_length=255,
        verbose_name='Nombre del Archivo',
        help_text='Nombre original del archivo'
    )
    
    archivo = models.FileField(
        upload_to=upload_to_adjuntos,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            )
        ],
        verbose_name='Archivo',
        help_text='Archivo adjunto al caso'
    )
    
    tipo_archivo = models.CharField(
        max_length=10,
        choices=[
            ('documento', 'Documento'),
            ('imagen', 'Imagen'),
            ('evidencia', 'Evidencia'),
            ('otro', 'Otro'),
        ],
        default='documento',
        verbose_name='Tipo de Archivo',
        help_text='Tipo de archivo adjunto'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción',
        help_text='Descripción del contenido del archivo'
    )
    
    tamaño_archivo = models.PositiveIntegerField(
        verbose_name='Tamaño del Archivo',
        help_text='Tamaño del archivo en bytes'
    )
    
    subido_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Subido por',
        help_text='Usuario que subió el archivo'
    )
    
    fecha_subida = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Subida',
        help_text='Fecha y hora en que se subió el archivo'
    )
    
    es_publico = models.BooleanField(
        default=True,
        verbose_name='Es Público',
        help_text='Si el archivo es visible para todas las partes del caso'
    )
    
    class Meta:
        verbose_name = 'Archivo Adjunto'
        verbose_name_plural = 'Archivos Adjuntos'
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre_archivo} - {self.caso.numero_caso}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para calcular el tamaño del archivo
        """
        if self.archivo:
            self.tamaño_archivo = self.archivo.size
        super().save(*args, **kwargs)
    
    def obtener_tamaño_formateado(self):
        """
        Retorna el tamaño del archivo en formato legible
        """
        tamaño = self.tamaño_archivo
        for unidad in ['B', 'KB', 'MB', 'GB']:
            if tamaño < 1024.0:
                return f"{tamaño:.1f} {unidad}"
            tamaño /= 1024.0
        return f"{tamaño:.1f} TB"


class Observacion(models.Model):
    """
    Modelo para observaciones y notas del caso
    Permite agregar comentarios y seguimiento del caso
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID de la Observación'
    )
    
    caso = models.ForeignKey(
        Caso,
        on_delete=models.CASCADE,
        related_name='observaciones',
        verbose_name='Caso',
        help_text='Caso al que pertenece la observación'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario',
        help_text='Usuario que agregó la observación'
    )
    
    contenido = models.TextField(
        verbose_name='Contenido',
        help_text='Contenido de la observación'
    )
    
    es_interna = models.BooleanField(
        default=False,
        verbose_name='Es Interna',
        help_text='Si la observación es solo para uso interno'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación',
        help_text='Fecha y hora en que se creó la observación'
    )
    
    class Meta:
        verbose_name = 'Observación'
        verbose_name_plural = 'Observaciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Observación - {self.caso.numero_caso} - {self.fecha_creacion.strftime('%d/%m/%Y')}"


class ConfiguracionSistema(models.Model):
    """
    Modelo para configuración general del sistema
    Permite personalizar aspectos del sistema
    """
    
    nombre_sistema = models.CharField(
        max_length=100,
        default='Sistema de Gestión de Casos Comunitarios - Jueces de Paz',
        verbose_name='Nombre del Sistema',
        help_text='Nombre que aparece en el sistema'
    )
    
    logo_sistema = models.ImageField(
        upload_to='configuracion/',
        blank=True,
        null=True,
        verbose_name='Logo del Sistema',
        help_text='Logo que aparece en el sistema'
    )
    
    color_primario = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Color Primario',
        help_text='Color primario del sistema (formato hexadecimal)'
    )
    
    color_secundario = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name='Color Secundario',
        help_text='Color secundario del sistema (formato hexadecimal)'
    )
    
    texto_pie_pagina = models.TextField(
        default='© 2024 Sistema de Gestión de Casos Comunitarios - Jueces de Paz',
        verbose_name='Texto del Pie de Página',
        help_text='Texto que aparece en el pie de página'
    )
    
    # Configuración de plazos
    plazo_estandar_dias = models.PositiveIntegerField(
        default=15,
        verbose_name='Plazo Estándar (días)',
        help_text='Plazo estándar para resolver casos en días'
    )
    
    plazo_prorroga_dias = models.PositiveIntegerField(
        default=15,
        verbose_name='Plazo de Prórroga (días)',
        help_text='Plazo adicional por prórroga en días'
    )
    
    dias_alerta_urgente = models.PositiveIntegerField(
        default=10,
        verbose_name='Días de Alerta Urgente',
        help_text='Días antes del vencimiento para mostrar alerta urgente'
    )
    
    # Configuración de archivos
    tamaño_maximo_archivo_mb = models.PositiveIntegerField(
        default=10,
        verbose_name='Tamaño Máximo de Archivo (MB)',
        help_text='Tamaño máximo permitido para archivos adjuntos en MB'
    )
    
    tipos_archivo_permitidos = models.CharField(
        max_length=100,
        default='pdf,doc,docx,jpg,jpeg,png',
        verbose_name='Tipos de Archivo Permitidos',
        help_text='Tipos de archivo permitidos separados por comas'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización',
        help_text='Última vez que se actualizó la configuración'
    )
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
    
    def __str__(self):
        return f"Configuración - {self.nombre_sistema}"
    
    @classmethod
    def obtener_configuracion(cls):
        """
        Obtiene la configuración del sistema, creando una instancia por defecto si no existe
        """
        configuracion, creada = cls.objects.get_or_create(
            pk=1,
            defaults={
                'nombre_sistema': 'Sistema de Gestión de Casos Comunitarios - Jueces de Paz',
                'color_primario': '#007bff',
                'color_secundario': '#6c757d',
                'texto_pie_pagina': '© 2024 Sistema de Gestión de Casos Comunitarios - Jueces de Paz',
            }
        )
        return configuracion
