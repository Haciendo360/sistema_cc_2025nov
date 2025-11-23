"""
Vistas para la aplicación de casos

Este archivo contiene todas las vistas relacionadas con la gestión de casos comunitarios:
- Panel del juez (listado y gestión de casos)
- Panel del administrador (métricas y supervisión)
- Gestión de casos (crear, editar, ver detalles)
- Gestión de archivos adjuntos
- Observaciones y seguimiento
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings
import csv
from datetime import datetime, timedelta

from .models import Caso, Adjunto, Observacion, ConfiguracionSistema
from usuarios.models import Usuario, Auditoria
from .forms import CasoForm, AdjuntoForm, ObservacionForm


@login_required
def panel_juez_view(request):
    """
    Panel principal del juez de paz
    Muestra sus casos asignados con métricas básicas
    """
    if not request.user.es_juez():
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('usuarios:login')
    
    # Obtener casos del juez
    casos = Caso.objects.filter(juez_asignado=request.user).order_by('-fecha_registro')
    
    # Métricas básicas
    total_casos = casos.count()
    casos_en_tramite = casos.filter(estado='en_tramite').count()
    casos_resueltos = casos.filter(estado='resuelto').count()
    casos_no_resueltos = casos.filter(estado='no_resuelto').count()
    
    # Casos urgentes y vencidos
    casos_urgentes = []
    casos_vencidos = []
    
    for caso in casos.filter(estado='en_tramite'):
        estado_urgente = caso.obtener_estado_urgente()
        if estado_urgente == 'urgente':
            casos_urgentes.append(caso)
        elif estado_urgente == 'vencido':
            casos_vencidos.append(caso)
    
    # Paginación para casos recientes
    casos_recientes = casos[:10]  # Últimos 10 casos
    
    context = {
        'total_casos': total_casos,
        'casos_en_tramite': casos_en_tramite,
        'casos_resueltos': casos_resueltos,
        'casos_no_resueltos': casos_no_resueltos,
        'casos_urgentes': casos_urgentes,
        'casos_vencidos': casos_vencidos,
        'casos_recientes': casos_recientes,
    }
    
    return render(request, 'casos/panel_juez.html', context)


@login_required
def panel_admin_view(request):
    """
    Panel principal del administrador
    Muestra métricas estadísticas y supervisión de todos los casos
    """
    if not request.user.es_admin():
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('usuarios:login')
    
    # Métricas generales
    total_casos = Caso.objects.count()
    casos_en_tramite = Caso.objects.filter(estado='en_tramite').count()
    casos_resueltos = Caso.objects.filter(estado='resuelto').count()
    casos_no_resueltos = Caso.objects.filter(estado='no_resuelto').count()
    
    # Usuarios pendientes de aprobación
    usuarios_pendientes = Usuario.objects.filter(estado_aprobacion='pendiente').count()
    
    # Casos por tipo de conflicto
    casos_por_tipo = list(Caso.objects.values('tipo_conflicto').annotate(
        total=Count('id')
    ).order_by('-total'))
    
    # Casos por bloque residencial
    casos_por_bloque = list(Caso.objects.values('bloque_residencial').annotate(
        total=Count('id')
    ).order_by('-total'))
    
    # Actividad mensual (últimos 6 meses)
    fecha_inicio = timezone.now() - timedelta(days=180)
    actividad_mensual = []
    
    for i in range(6):
        fecha = timezone.now() - timedelta(days=30*i)
        mes_inicio = fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mes_fin = mes_inicio + timedelta(days=32)
        mes_fin = mes_fin.replace(day=1) - timedelta(days=1)
        
        casos_mes = Caso.objects.filter(
            fecha_registro__gte=mes_inicio,
            fecha_registro__lte=mes_fin
        ).count()
        
        actividad_mensual.append({
            'mes': mes_inicio.strftime('%Y-%m'),
            'total': casos_mes
        })
    
    actividad_mensual.reverse()
    
    # Casos recientes
    casos_recientes = Caso.objects.order_by('-fecha_registro')[:10]
    
    context = {
        'total_casos': total_casos,
        'casos_en_tramite': casos_en_tramite,
        'casos_resueltos': casos_resueltos,
        'casos_no_resueltos': casos_no_resueltos,
        'usuarios_pendientes': usuarios_pendientes,
        'casos_por_tipo': casos_por_tipo,
        'casos_por_bloque': casos_por_bloque,
        'actividad_mensual': actividad_mensual,
        'casos_recientes': casos_recientes,
    }
    
    return render(request, 'casos/panel_admin.html', context)


@login_required
def listado_casos_view(request):
    """
    Listado de casos con filtros y búsqueda
    """
    if not request.user.puede_acceder_sistema():
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('usuarios:login')
    
    # Filtrar casos según el rol del usuario
    if request.user.es_juez():
        casos = Caso.objects.filter(juez_asignado=request.user)
    else:
        casos = Caso.objects.all()
    
    # Aplicar filtros
    estado = request.GET.get('estado', '')
    tipo_conflicto = request.GET.get('tipo_conflicto', '')
    bloque = request.GET.get('bloque', '')
    busqueda = request.GET.get('busqueda', '')
    
    if estado:
        casos = casos.filter(estado=estado)
    
    if tipo_conflicto:
        casos = casos.filter(tipo_conflicto=tipo_conflicto)
    
    if bloque:
        casos = casos.filter(bloque_residencial=bloque)
    
    if busqueda:
        casos = casos.filter(
            Q(numero_caso__icontains=busqueda) |
            Q(nombre_solicitante__icontains=busqueda) |
            Q(cedula_solicitante__icontains=busqueda) |
            Q(nombre_involucrado__icontains=busqueda)
        )
    
    # Ordenar por fecha de registro (más recientes primero)
    casos = casos.order_by('-fecha_registro')
    
    # Paginación
    paginator = Paginator(casos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'estado': estado,
        'tipo_conflicto': tipo_conflicto,
        'bloque': bloque,
        'busqueda': busqueda,
        'estados': Caso.ESTADO_CHOICES,
        'tipos_conflicto': Caso.TIPO_CONFLICTO_CHOICES,
        'bloques': [
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
            ('BLOQUE_25', 'Bloque 25'),
        ],
    }
    
    return render(request, 'casos/listado_casos.html', context)


@login_required
def crear_caso_view(request):
    """
    Vista para crear un nuevo caso
    """
    if not request.user.es_juez():
        messages.error(request, 'Solo los jueces de paz pueden crear casos.')
        return redirect('casos:listado_casos')
    
    if request.method == 'POST':
        form = CasoForm(request.POST)
        if form.is_valid():
            caso = form.save(commit=False)
            caso.juez_asignado = request.user
            caso.creado_por = request.user
            
            # Asegurar que la fecha de registro esté establecida
            if not caso.fecha_registro:
                caso.fecha_registro = timezone.now()
            
            # Calcular fecha límite manualmente si no está establecida
            if not caso.fecha_limite:
                caso.fecha_limite = caso.fecha_registro + timezone.timedelta(
                    days=settings.PLAZO_ESTANDAR_DIAS
                )
            
            caso.save()
            
            # Registrar en auditoría
            Auditoria.registrar_accion(
                usuario=request.user,
                accion='crear',
                modelo_afectado='Caso',
                objeto_id=str(caso.id),
                descripcion=f'Nuevo caso creado: {caso.numero_caso}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'Caso {caso.numero_caso} creado exitosamente.')
            return redirect('casos:detalle_caso', caso_id=caso.id)
    else:
        form = CasoForm()
    
    return render(request, 'casos/crear_caso.html', {'form': form})


@login_required
def detalle_caso_view(request, caso_id):
    """
    Vista para ver los detalles de un caso
    """
    caso = get_object_or_404(Caso, id=caso_id)
    
    # Verificar permisos
    if request.user.es_juez() and caso.juez_asignado != request.user:
        messages.error(request, 'No tienes permisos para ver este caso.')
        return redirect('casos:listado_casos')
    
    # Obtener adjuntos y observaciones
    adjuntos = caso.adjuntos.all().order_by('-fecha_subida')
    observaciones = caso.observaciones.all().order_by('-fecha_creacion')
    
    # Calcular progreso y estado urgente
    progreso = caso.calcular_progreso()
    estado_urgente = caso.obtener_estado_urgente()
    
    context = {
        'caso': caso,
        'adjuntos': adjuntos,
        'observaciones': observaciones,
        'progreso': progreso,
        'estado_urgente': estado_urgente,
    }
    
    return render(request, 'casos/detalle_caso.html', context)


@login_required
def editar_caso_view(request, caso_id):
    """
    Vista para editar un caso existente
    """
    caso = get_object_or_404(Caso, id=caso_id)
    
    # Verificar permisos
    if request.user.es_juez() and caso.juez_asignado != request.user:
        messages.error(request, 'No tienes permisos para editar este caso.')
        return redirect('casos:listado_casos')
    
    if request.method == 'POST':
        form = CasoForm(request.POST, instance=caso)
        if form.is_valid():
            caso_actualizado = form.save()
            messages.success(request, f'Caso {caso.numero_caso} actualizado correctamente.')
            return redirect('casos:detalle_caso', caso_id=caso_actualizado.id)
        else:
            # Si el formulario no es válido, mostrar errores en la consola
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"ERROR en campo {field}: {error}")
    else:
        form = CasoForm(instance=caso)
    
    # Pasar errores del formulario al contexto
    context = {
        'form': form, 
        'caso': caso,
        'form_errors': form.errors if request.method == 'POST' else {}
    }
    return render(request, 'casos/editar_caso.html', context)


@login_required
def eliminar_caso_view(request, caso_id):
    """
    Vista para eliminar un caso (solo administradores)
    """
    if not request.user.es_admin():
        messages.error(request, 'Solo los administradores pueden eliminar casos.')
        return redirect('casos:listado_casos')
    
    caso = get_object_or_404(Caso, id=caso_id)
    
    if request.method == 'POST':
        numero_caso = caso.numero_caso
        caso.delete()
        messages.success(request, f'Caso {numero_caso} eliminado correctamente.')
        return redirect('casos:listado_casos')
    
    return render(request, 'casos/eliminar_caso.html', {'caso': caso})


@login_required
def cambiar_estado_caso_view(request, caso_id):
    """
    Vista para cambiar el estado de un caso
    """
    caso = get_object_or_404(Caso, id=caso_id)
    
    # Verificar permisos
    if request.user.es_juez() and caso.juez_asignado != request.user:
        messages.error(request, 'No tienes permisos para modificar este caso.')
        return redirect('casos:listado_casos')
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        medio_resolucion = request.POST.get('medio_resolucion')
        observaciones = request.POST.get('observaciones_resolucion')
        
        caso.estado = nuevo_estado
        
        if nuevo_estado in ['resuelto', 'no_resuelto']:
            caso.medio_resolucion = medio_resolucion
            caso.observaciones_resolucion = observaciones
            caso.fecha_resolucion = timezone.now()
            
            if nuevo_estado == 'no_resuelto':
                caso.fecha_cierre = timezone.now()
        
        caso.save()
        
        messages.success(request, f'Estado del caso {caso.numero_caso} actualizado correctamente.')
        return redirect('casos:detalle_caso', caso_id=caso.id)
    
    return render(request, 'casos/cambiar_estado_caso.html', {'caso': caso})


@login_required
def solicitar_prorroga_view(request, caso_id):
    """
    Vista para solicitar prórroga de un caso
    """
    caso = get_object_or_404(Caso, id=caso_id)
    
    # Verificar permisos
    if request.user.es_juez() and caso.juez_asignado != request.user:
        messages.error(request, 'No tienes permisos para solicitar prórroga para este caso.')
        return redirect('casos:listado_casos')
    
    if not caso.puede_solicitar_prorroga():
        messages.error(request, 'Este caso no puede solicitar prórroga.')
        return redirect('casos:detalle_caso', caso_id=caso.id)
    
    if request.method == 'POST':
        justificacion = request.POST.get('justificacion')
        
        if caso.solicitar_prorroga(justificacion, request.user):
            messages.success(request, f'Prórroga solicitada para el caso {caso.numero_caso}.')
            return redirect('casos:detalle_caso', caso_id=caso.id)
        else:
            messages.error(request, 'No se pudo solicitar la prórroga.')
    
    return render(request, 'casos/solicitar_prorroga.html', {'caso': caso})


@login_required
def gestion_adjuntos_view(request, caso_id):
    """
    Vista para gestionar archivos adjuntos de un caso
    """
    caso = get_object_or_404(Caso, id=caso_id)
    
    # Verificar permisos
    if request.user.es_juez() and caso.juez_asignado != request.user:
        messages.error(request, 'No tienes permisos para gestionar archivos de este caso.')
        return redirect('casos:listado_casos')
    
    adjuntos = caso.adjuntos.all().order_by('-fecha_subida')
    
    return render(request, 'casos/gestion_adjuntos.html', {'caso': caso, 'adjuntos': adjuntos})


@login_required
def subir_adjunto_view(request, caso_id):
    """
    Vista para subir un archivo adjunto
    """
    caso = get_object_or_404(Caso, id=caso_id)
    
    # Verificar permisos
    if request.user.es_juez() and caso.juez_asignado != request.user:
        messages.error(request, 'No tienes permisos para subir archivos a este caso.')
        return redirect('casos:listado_casos')
    
    if request.method == 'POST':
        form = AdjuntoForm(request.POST, request.FILES)
        if form.is_valid():
            adjunto = form.save(commit=False)
            adjunto.caso = caso
            adjunto.subido_por = request.user
            adjunto.save()
            
            messages.success(request, 'Archivo subido correctamente.')
            return redirect('casos:gestion_adjuntos', caso_id=caso.id)
    else:
        form = AdjuntoForm()
    
    return render(request, 'casos/subir_adjunto.html', {'form': form, 'caso': caso})


@login_required
def descargar_adjunto_view(request, adjunto_id):
    """
    Vista para descargar un archivo adjunto
    """
    adjunto = get_object_or_404(Adjunto, id=adjunto_id)
    
    # Verificar permisos
    if request.user.es_juez() and adjunto.caso.juez_asignado != request.user:
        messages.error(request, 'No tienes permisos para descargar este archivo.')
        return redirect('casos:listado_casos')
    
    response = HttpResponse(adjunto.archivo.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{adjunto.nombre_archivo}"'
    return response


@login_required
def eliminar_adjunto_view(request, adjunto_id):
    """
    Vista para eliminar un archivo adjunto
    """
    adjunto = get_object_or_404(Adjunto, id=adjunto_id)
    
    # Verificar permisos
    if request.user.es_juez() and adjunto.subido_por != request.user:
        messages.error(request, 'No tienes permisos para eliminar este archivo.')
        return redirect('casos:listado_casos')
    
    if request.method == 'POST':
        adjunto.delete()
        messages.success(request, 'Archivo eliminado correctamente.')
        return redirect('casos:gestion_adjuntos', caso_id=adjunto.caso.id)
    
    return render(request, 'casos/eliminar_adjunto.html', {'adjunto': adjunto})


@login_required
def observaciones_caso_view(request, caso_id):
    """
    Vista para ver observaciones de un caso
    """
    caso = get_object_or_404(Caso, id=caso_id)
    
    # Verificar permisos
    if request.user.es_juez() and caso.juez_asignado != request.user:
        messages.error(request, 'No tienes permisos para ver observaciones de este caso.')
        return redirect('casos:listado_casos')
    
    observaciones = caso.observaciones.all().order_by('-fecha_creacion')
    
    return render(request, 'casos/observaciones_caso.html', {'caso': caso, 'observaciones': observaciones})


@login_required
def agregar_observacion_view(request, caso_id):
    """
    Vista para agregar una observación a un caso
    """
    caso = get_object_or_404(Caso, id=caso_id)
    
    # Verificar permisos
    if request.user.es_juez() and caso.juez_asignado != request.user:
        messages.error(request, 'No tienes permisos para agregar observaciones a este caso.')
        return redirect('casos:listado_casos')
    
    if request.method == 'POST':
        form = ObservacionForm(request.POST)
        if form.is_valid():
            observacion = form.save(commit=False)
            observacion.caso = caso
            observacion.usuario = request.user
            observacion.save()
            
            messages.success(request, 'Observación agregada correctamente.')
            return redirect('casos:observaciones_caso', caso_id=caso.id)
    else:
        form = ObservacionForm()
    
    return render(request, 'casos/agregar_observacion.html', {'form': form, 'caso': caso})


@login_required
def reportes_view(request):
    """
    Vista para generar reportes (solo administradores)
    """
    if not request.user.es_admin():
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('casos:panel_juez')
    
    return render(request, 'casos/reportes.html')


@login_required
def exportar_csv_view(request):
    """
    Vista para exportar datos en formato CSV
    """
    if not request.user.es_admin():
        messages.error(request, 'No tienes permisos para exportar datos.')
        return redirect('casos:panel_juez')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="casos_comunitarios.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Número de Caso', 'Solicitante', 'Cédula Solicitante', 'Juez Asignado',
        'Tipo de Conflicto', 'Bloque Residencial', 'Estado', 'Fecha de Registro',
        'Fecha Límite', 'Fecha de Resolución'
    ])
    
    casos = Caso.objects.all().select_related('juez_asignado')
    for caso in casos:
        writer.writerow([
            caso.numero_caso,
            caso.nombre_solicitante,
            caso.cedula_solicitante,
            caso.juez_asignado.get_full_name(),
            caso.get_tipo_conflicto_display(),
            caso.get_bloque_residencial_display(),
            caso.get_estado_display(),
            caso.fecha_registro.strftime('%d/%m/%Y'),
            caso.fecha_limite.strftime('%d/%m/%Y'),
            caso.fecha_resolucion.strftime('%d/%m/%Y') if caso.fecha_resolucion else ''
        ])
    
    return response


# API endpoints para gráficos (AJAX)
@login_required
def api_estadisticas_casos(request):
    """
    API endpoint para estadísticas generales de casos
    """
    if not request.user.es_admin():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    total_casos = Caso.objects.count()
    casos_en_tramite = Caso.objects.filter(estado='en_tramite').count()
    casos_resueltos = Caso.objects.filter(estado='resuelto').count()
    casos_no_resueltos = Caso.objects.filter(estado='no_resuelto').count()
    
    return JsonResponse({
        'total_casos': total_casos,
        'casos_en_tramite': casos_en_tramite,
        'casos_resueltos': casos_resueltos,
        'casos_no_resueltos': casos_no_resueltos,
    })


@login_required
def api_casos_por_estado(request):
    """
    API endpoint para casos por estado
    """
    if not request.user.es_admin():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    casos_por_estado = Caso.objects.values('estado').annotate(total=Count('id'))
    
    return JsonResponse({
        'labels': [item['estado'] for item in casos_por_estado],
        'data': [item['total'] for item in casos_por_estado]
    })


@login_required
def api_casos_por_tipo(request):
    """
    API endpoint para casos por tipo de conflicto
    """
    if not request.user.es_admin():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    casos_por_tipo = Caso.objects.values('tipo_conflicto').annotate(total=Count('id'))
    
    return JsonResponse({
        'labels': [item['tipo_conflicto'] for item in casos_por_tipo],
        'data': [item['total'] for item in casos_por_tipo]
    })


@login_required
def api_casos_por_bloque(request):
    """
    API endpoint para casos por bloque residencial
    """
    if not request.user.es_admin():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    casos_por_bloque = Caso.objects.values('bloque_residencial').annotate(total=Count('id'))
    
    return JsonResponse({
        'labels': [item['bloque_residencial'] for item in casos_por_bloque],
        'data': [item['total'] for item in casos_por_bloque]
    })


@login_required
def api_actividad_mensual(request):
    """
    API endpoint para actividad mensual
    """
    if not request.user.es_admin():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Últimos 6 meses
    from datetime import datetime, timedelta
    fecha_inicio = timezone.now() - timedelta(days=180)
    actividad_mensual = []
    
    for i in range(6):
        fecha = timezone.now() - timedelta(days=30*i)
        mes_inicio = fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mes_fin = mes_inicio + timedelta(days=32)
        mes_fin = mes_fin.replace(day=1) - timedelta(days=1)
        
        casos_mes = Caso.objects.filter(
            fecha_registro__gte=mes_inicio,
            fecha_registro__lte=mes_fin
        ).count()
        
        actividad_mensual.append({
            'mes': mes_inicio.strftime('%Y-%m'),
            'total': casos_mes
        })
    
    actividad_mensual.reverse()
    
    return JsonResponse({
        'labels': [item['mes'] for item in actividad_mensual],
        'data': [item['total'] for item in actividad_mensual]
    })