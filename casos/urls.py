"""
URLs para la aplicación de casos

Este archivo contiene todas las rutas relacionadas con la gestión de casos comunitarios:
- Panel del juez (listado y gestión de casos)
- Panel del administrador (métricas y supervisión)
- Gestión de casos (crear, editar, ver detalles)
- Gestión de archivos adjuntos
- Observaciones y seguimiento
"""

from django.urls import path
from . import views

app_name = 'casos'

urlpatterns = [
    # Panel principal del juez
    path('panel-juez/', views.panel_juez_view, name='panel_juez'),
    
    # Panel principal del administrador
    path('panel-admin/', views.panel_admin_view, name='panel_admin'),
    
    # Gestión de casos
    path('', views.listado_casos_view, name='listado_casos'),
    path('crear/', views.crear_caso_view, name='crear_caso'),
    path('<uuid:caso_id>/', views.detalle_caso_view, name='detalle_caso'),
    path('<uuid:caso_id>/editar/', views.editar_caso_view, name='editar_caso'),
    path('<uuid:caso_id>/eliminar/', views.eliminar_caso_view, name='eliminar_caso'),
    
    # Gestión de estados de casos
    path('<uuid:caso_id>/cambiar-estado/', views.cambiar_estado_caso_view, name='cambiar_estado_caso'),
    path('<uuid:caso_id>/solicitar-prorroga/', views.solicitar_prorroga_view, name='solicitar_prorroga'),
    
    # Gestión de archivos adjuntos
    path('<uuid:caso_id>/adjuntos/', views.gestion_adjuntos_view, name='gestion_adjuntos'),
    path('<uuid:caso_id>/adjuntos/subir/', views.subir_adjunto_view, name='subir_adjunto'),
    path('adjuntos/<uuid:adjunto_id>/descargar/', views.descargar_adjunto_view, name='descargar_adjunto'),
    path('adjuntos/<uuid:adjunto_id>/eliminar/', views.eliminar_adjunto_view, name='eliminar_adjunto'),
    
    # Observaciones
    path('<uuid:caso_id>/observaciones/', views.observaciones_caso_view, name='observaciones_caso'),
    path('<uuid:caso_id>/observaciones/agregar/', views.agregar_observacion_view, name='agregar_observacion'),
    
    # Reportes y estadísticas
    path('reportes/', views.reportes_view, name='reportes'),
    path('reportes/exportar-csv/', views.exportar_csv_view, name='exportar_csv'),
    
    # API endpoints para gráficos (AJAX)
    path('api/estadisticas-casos/', views.api_estadisticas_casos, name='api_estadisticas_casos'),
    path('api/casos-por-estado/', views.api_casos_por_estado, name='api_casos_por_estado'),
    path('api/casos-por-tipo/', views.api_casos_por_tipo, name='api_casos_por_tipo'),
    path('api/casos-por-bloque/', views.api_casos_por_bloque, name='api_casos_por_bloque'),
    path('api/actividad-mensual/', views.api_actividad_mensual, name='api_actividad_mensual'),
]
