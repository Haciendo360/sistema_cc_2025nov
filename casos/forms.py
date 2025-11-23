"""
Formularios para la aplicación de casos

Este archivo contiene todos los formularios necesarios para la gestión de casos:
- Formulario de caso
- Formulario de adjunto
- Formulario de observación
"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import Caso, Adjunto, Observacion


class CasoForm(forms.ModelForm):
    """
    Formulario para crear y editar casos comunitarios
    """
    
    class Meta:
        model = Caso
        fields = [
            'cedula_solicitante', 'nombre_solicitante', 'telefono_solicitante', 'direccion_solicitante',
            'cedula_involucrado', 'nombre_involucrado', 'telefono_involucrado', 'direccion_involucrado',
            'tipo_conflicto', 'descripcion_caso', 'bloque_residencial'
        ]
        widgets = {
            'cedula_solicitante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890',
                'maxlength': '10',
                'pattern': '[0-9]{10}',
                'title': 'Ingrese exactamente 10 dígitos'
            }),
            'nombre_solicitante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del solicitante'
            }),
            'telefono_solicitante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0987654321'
            }),
            'direccion_solicitante': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa del solicitante'
            }),
            'cedula_involucrado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890',
                'maxlength': '10',
                'pattern': '[0-9]{10}',
                'title': 'Ingrese exactamente 10 dígitos'
            }),
            'nombre_involucrado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del involucrado'
            }),
            'telefono_involucrado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0987654321'
            }),
            'direccion_involucrado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa del involucrado'
            }),
            'tipo_conflicto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion_caso': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descripción detallada del conflicto presentado'
            }),
            'bloque_residencial': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def clean_cedula_solicitante(self):
        """
        Validar formato de cédula del solicitante
        """
        cedula = self.cleaned_data.get('cedula_solicitante')
        if cedula and len(cedula) != 10:
            raise ValidationError('La cédula debe tener exactamente 10 dígitos.')
        return cedula
    
    def clean_cedula_involucrado(self):
        """
        Validar formato de cédula del involucrado
        """
        cedula = self.cleaned_data.get('cedula_involucrado')
        if cedula and len(cedula) != 10:
            raise ValidationError('La cédula debe tener exactamente 10 dígitos.')
        return cedula


class AdjuntoForm(forms.ModelForm):
    """
    Formulario para subir archivos adjuntos a un caso
    """
    
    class Meta:
        model = Adjunto
        fields = ['nombre_archivo', 'archivo', 'tipo_archivo', 'descripcion', 'es_publico']
        widgets = {
            'nombre_archivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre descriptivo del archivo'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'tipo_archivo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del contenido del archivo'
            }),
            'es_publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_archivo(self):
        """
        Validar el archivo adjunto
        """
        archivo = self.cleaned_data.get('archivo')
        
        if archivo:
            # Validar tamaño (10MB máximo)
            max_size = 10 * 1024 * 1024  # 10MB en bytes
            if archivo.size > max_size:
                raise ValidationError('El archivo no puede ser mayor a 10MB.')
            
            # Validar tipo de archivo
            extensiones_permitidas = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            extension = archivo.name.split('.')[-1].lower()
            
            if extension not in extensiones_permitidas:
                raise ValidationError(
                    f'Tipo de archivo no permitido. Extensiones permitidas: {", ".join(extensiones_permitidas)}'
                )
        
        return archivo


class ObservacionForm(forms.ModelForm):
    """
    Formulario para agregar observaciones a un caso
    """
    
    class Meta:
        model = Observacion
        fields = ['contenido', 'es_interna']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escriba su observación aquí...'
            }),
            'es_interna': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_contenido(self):
        """
        Validar contenido de la observación
        """
        contenido = self.cleaned_data.get('contenido')
        
        if not contenido or len(contenido.strip()) < 10:
            raise ValidationError('La observación debe tener al menos 10 caracteres.')
        
        return contenido.strip()


class CambiarEstadoCasoForm(forms.Form):
    """
    Formulario para cambiar el estado de un caso
    """
    
    ESTADO_CHOICES = [
        ('en_tramite', 'En Trámite'),
        ('resuelto', 'Resuelto'),
        ('no_resuelto', 'No Resuelto'),
    ]
    
    nuevo_estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Nuevo Estado'
    )
    
    medio_resolucion = forms.ChoiceField(
        choices=Caso.MEDIO_RESOLUCION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Medio de Resolución'
    )
    
    observaciones_resolucion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones sobre la resolución del caso'
        }),
        label='Observaciones de Resolución'
    )


class SolicitarProrrogaForm(forms.Form):
    """
    Formulario para solicitar prórroga de un caso
    """
    
    justificacion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Justifique por qué necesita una prórroga para este caso...'
        }),
        label='Justificación de la Prórroga',
        help_text='Explique detalladamente por qué necesita más tiempo para resolver este caso.'
    )
    
    def clean_justificacion(self):
        """
        Validar justificación de la prórroga
        """
        justificacion = self.cleaned_data.get('justificacion')
        
        if not justificacion or len(justificacion.strip()) < 20:
            raise ValidationError('La justificación debe tener al menos 20 caracteres.')
        
        return justificacion.strip()
