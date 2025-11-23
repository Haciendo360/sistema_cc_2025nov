# Sistema de Gestión de Casos Comunitarios - Jueces de Paz

Una aplicación web completa desarrollada con Django para la gestión digital de casos comunitarios bajo la jurisdicción de Jueces de Paz.

## 🏛️ Descripción del Sistema

Este sistema automatiza y digitaliza el proceso de gestión de conflictos comunitarios, garantizando un seguimiento eficiente, transparente y oportuno de cada caso desde su registro hasta su resolución, cumpliendo con los plazos legales y mejorando la calidad del servicio de justicia comunitaria.

## 🎯 Características Principales

### ✅ Autenticación y Gestión de Usuarios
- **Registro con aprobación**: Los usuarios se registran pero quedan en estado "Pendiente" hasta que un administrador los aprueba
- **Roles diferenciados**:
  - **Juez de Paz**: Acceso a casos asignados, registro de nuevos casos, seguimiento de plazos
  - **Administrador**: Gestión de usuarios, supervisión de todos los casos, configuración del sistema
- **Recuperación de contraseña**: Sistema seguro con tokens expirables

### ✅ Gestión de Casos Comunitarios
- **Registro automático de casos**:
  - Número de caso auto-generado (formato: JC-AÑO-MES-XXXX)
  - Fecha de registro automática
  - Tipos de conflictos: Vecinal, Individual, Comunitario, Contravenciones, Obligaciones patrimoniales
- **Seguimiento de plazos**:
  - Plazo estándar: 15 días
  - Prórroga: +15 días (una sola vez)
  - Termómetro de progreso visual (0-100%)
  - Alertas visuales cuando el caso está "Urgente" o "Vencido"

### ✅ Panel del Administrador
- **Métricas estadísticas en tiempo real**:
  - Gráficos de casos por estado, tipo de conflicto, bloque residencial
  - Actividad mensual con tendencias
  - Resumen de métricas clave
- **Herramientas de gestión**:
  - Filtros avanzados y búsqueda rápida
  - Aprobación/rechazo de usuarios pendientes
  - Edición y eliminación de casos
  - Descarga de reportes en CSV

### ✅ Panel del Juez de Paz
- **Registro de nuevos casos** con formulario estructurado
- **Listado de casos asignados** ordenados por fecha
- **Gestión de archivos adjuntos**:
  - Subida de documentos (PDF, DOC, DOCX, JPG, PNG)
  - Límite de tamaño: 10MB por archivo
  - Historial de adjuntos con fecha y hora
- **Seguimiento visual**:
  - Termómetro de progreso basado en días transcurridos
  - Indicadores de estado (En tiempo, Urgente, Vencido)
  - Acciones permitidas (cambiar estado, solicitar prórroga)

### ✅ Seguridad y Auditoría
- **Control de acceso estricto** por roles
- **Auditoría completa** de todas las acciones
- **Cumplimiento de plazos legales** con alertas automáticas
- **Protección de datos** con encriptación y validación

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 4.2.7 (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Gráficos**: Chart.js para visualizaciones interactivas
- **Archivos**: Soporte para PDF, DOC, DOCX, JPG, PNG
- **Despliegue**: Render.com con Gunicorn

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- pip (gestor de paquetes de Python)
- Git

### Instalación Local

1. **Clonar el repositorio**:
```bash
git clone <url-del-repositorio>
cd sistema_casos_comunitario_curs
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
# Copiar archivo de ejemplo
cp env_example.txt .env

# Editar .env con tus configuraciones
# SECRET_KEY=tu-clave-secreta-super-segura
# DEBUG=True
# DATABASE_URL=sqlite:///db.sqlite3
```

5. **Ejecutar migraciones**:
```bash
python manage.py migrate
```

6. **Crear superusuario**:
```bash
python manage.py createsuperuser
```

7. **Ejecutar servidor de desarrollo**:
```bash
python manage.py runserver
```

8. **Acceder a la aplicación**:
   - Aplicación: http://127.0.0.1:8000/
   - Panel de administración: http://127.0.0.1:8000/admin/

### Despliegue en Render.com

1. **Crear cuenta en Render.com**
2. **Conectar repositorio de GitHub**
3. **Configurar servicio web**:
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn sistema_casos_comunitario.wsgi:application`
4. **Configurar variables de entorno**:
   - `SECRET_KEY`: Clave secreta de Django
   - `DEBUG`: False
   - `DATABASE_URL`: URL de PostgreSQL de Render
   - `ALLOWED_HOSTS`: tu-app.onrender.com
   - `CSRF_TRUSTED_ORIGINS`: https://tu-app.onrender.com
5. **Desplegar**

## 📁 Estructura del Proyecto

```
sistema_casos_comunitario_curs/
├── casos/                    # Aplicación de gestión de casos
│   ├── models.py            # Modelos de datos (Caso, Adjunto, Observacion)
│   ├── views.py             # Vistas del sistema
│   ├── forms.py             # Formularios
│   ├── urls.py              # URLs de casos
│   └── admin.py             # Configuración del admin
├── usuarios/                 # Aplicación de gestión de usuarios
│   ├── models.py            # Modelos de usuario personalizado
│   ├── views.py             # Vistas de autenticación
│   ├── forms.py             # Formularios de usuario
│   └── urls.py              # URLs de usuarios
├── sistema_casos_comunitario/ # Configuración principal
│   ├── settings.py          # Configuración de Django
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # Configuración WSGI
├── templates/               # Templates HTML
│   ├── base.html           # Template base
│   ├── usuarios/           # Templates de usuarios
│   └── casos/              # Templates de casos
├── static/                  # Archivos estáticos
├── media/                   # Archivos subidos por usuarios
├── requirements.txt         # Dependencias de Python
├── render.yaml             # Configuración para Render.com
└── manage.py               # Script de gestión de Django
```

## 👥 Roles y Permisos

### Juez de Paz
- Crear y gestionar casos asignados
- Subir archivos adjuntos
- Agregar observaciones
- Solicitar prórrogas
- Cambiar estado de casos

### Administrador
- Aprobar/rechazar usuarios
- Ver todos los casos del sistema
- Acceder a métricas estadísticas
- Generar reportes
- Configurar el sistema

## 📊 Funcionalidades de Seguimiento

### Plazos Legales
- **Plazo estándar**: 15 días para resolver casos
- **Prórroga**: 15 días adicionales (una sola vez por caso)
- **Alertas**: Notificaciones visuales a los 10 días

### Estados de Casos
- **En Trámite**: Caso activo siendo procesado
- **Resuelto**: Caso resuelto pero no cerrado
- **Cerrado**: Caso finalizado definitivamente
- **Archivado**: Caso archivado por motivos especiales

### Indicadores Visuales
- **✅ En tiempo**: 0-9 días transcurridos
- **⚠️ Urgente**: 10-14 días transcurridos
- **❌ Vencido**: 15+ días transcurridos

## 🔧 Configuración Avanzada

### Personalización del Sistema
- Logo y colores personalizables
- Texto del pie de página configurable
- Plazos legales ajustables
- Límites de archivos modificables

### Integración de Email
- Configuración SMTP para notificaciones
- Recuperación de contraseñas por email
- Alertas automáticas de vencimiento

## 📈 Métricas y Reportes

### Panel de Administrador
- Gráfico de casos por estado
- Distribución por tipo de conflicto
- Actividad por bloque residencial
- Tendencia mensual de casos
- Porcentaje de cumplimiento de plazos

### Exportación de Datos
- Reportes en formato CSV
- Filtros avanzados para exportación
- Datos completos de casos y usuarios

## 🛡️ Seguridad

### Medidas Implementadas
- Autenticación robusta con roles
- Validación de datos en cliente y servidor
- Protección CSRF
- Encriptación de contraseñas
- Auditoría completa de acciones
- Control de acceso por roles

### Cumplimiento Legal
- Seguimiento estricto de plazos legales
- Registro de prórrogas con justificación
- Trazabilidad completa de procesos
- Archivo seguro de documentos

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📝 Licencia

Este proyecto está desarrollado para uso institucional en el sistema de justicia comunitaria.

## 📞 Soporte

Para soporte técnico o consultas sobre el sistema, contacte al equipo de desarrollo.

---

**Desarrollado con Django 4.2.7** | **Sistema de Gestión de Casos Comunitarios - Jueces de Paz**
