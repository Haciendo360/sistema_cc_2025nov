"""
Formularios para la aplicación de usuarios

Este archivo contiene todos los formularios necesarios para la gestión de usuarios:
- Formulario de login
- Formulario de registro
- Formulario de perfil
- Formularios de cambio de contraseña
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import Usuario, PerfilUsuario


class LoginForm(forms.Form):
    """
    Formulario para el login de usuarios
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'required': True
        }),
        label='Nombre de Usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'required': True
        }),
        label='Contraseña'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Recordarme'
    )


class RegistroForm(UserCreationForm):
    """
    Formulario para el registro de nuevos usuarios
    """
    
    # Campos adicionales al formulario base
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombres',
            'required': True
        }),
        label='Nombres'
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos',
            'required': True
        }),
        label='Apellidos'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'required': True
        }),
        label='Correo Electrónico'
    )
    
    cedula = forms.CharField(
        max_length=10,
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message='La cédula debe tener exactamente 10 dígitos'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234567890',
            'required': True
        }),
        label='Cédula de Identidad'
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0987654321'
        }),
        label='Teléfono'
    )
    
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Dirección de residencia'
        }),
        label='Dirección'
    )
    
    rol = forms.ChoiceField(
        choices=Usuario.ROL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Rol',
        initial='juez'
    )
    
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'cedula', 
                 'telefono', 'direccion', 'rol', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        
        # Personalizar campo de username
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
    
    def clean_cedula(self):
        """
        Validar que la cédula no esté registrada
        """
        cedula = self.cleaned_data.get('cedula')
        if cedula and Usuario.objects.filter(cedula=cedula).exists():
            raise ValidationError('Ya existe un usuario con esta cédula.')
        return cedula
    
    def clean_email(self):
        """
        Validar que el email no esté registrado
        """
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        return email


class PerfilForm(forms.ModelForm):
    """
    Formulario para editar el perfil de usuario
    """
    
    class Meta:
        model = PerfilUsuario
        fields = ['avatar', 'biografia', 'especialidad', 'años_experiencia',
                 'recibir_notificaciones_email', 'recibir_alertas_casos', 'tema_preferido']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Breve descripción personal...'
            }),
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especialidad o área de conocimiento'
            }),
            'años_experiencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'recibir_notificaciones_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'recibir_alertas_casos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tema_preferido': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class CambiarPasswordForm(PasswordChangeForm):
    """
    Formulario para cambiar la contraseña del usuario actual
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar campos
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })


class RecuperarPasswordForm(forms.Form):
    """
    Formulario para solicitar recuperación de contraseña
    """
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'required': True
        }),
        label='Correo Electrónico'
    )


class ResetPasswordForm(forms.Form):
    """
    Formulario para restablecer la contraseña con token
    """
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña',
            'required': True
        }),
        label='Nueva Contraseña'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña',
            'required': True
        }),
        label='Confirmar Nueva Contraseña'
    )
    
    def clean(self):
        """
        Validar que las contraseñas coincidan
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data
