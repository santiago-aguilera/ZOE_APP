"""
Rutas del blueprint de Cronograma.
Maneja la visualización del calendario de eventos.
"""

import calendar as calendar_lib
from datetime import date

from flask import render_template, request, session, redirect, url_for, flash

from app.blueprints import cronograma_bp
from app.models import Cronograma, Tarea, Mensaje, Grupo, Usuario, Entrega, Materia, Curso
from app.decorators import login_required, modulo_requerido, eliminacion_segura


def _construir_calendario_mes(anio: int, mes: int, eventos: list) -> list:
    """Arma matriz de semanas x días y marca eventos."""
    eventos_por_dia = {}
    for ev in eventos:
        if not ev.fecha_evento:
            continue
        fecha_ev = ev.fecha_evento
        if hasattr(fecha_ev, 'date'):
            fecha_ev = fecha_ev.date()
        if fecha_ev.year == anio and fecha_ev.month == mes:
            eventos_por_dia.setdefault(fecha_ev.day, []).append(ev.titulo)

    matriz_dias = calendar_lib.monthcalendar(anio, mes)
    calendario = []
    for semana in matriz_dias:
        fila = []
        for dia_numero in semana:
            if dia_numero == 0:
                fila.append({'numero': '', 'evento': False})
            else:
                fila.append({
                    'numero': dia_numero,
                    'evento': dia_numero in eventos_por_dia
                })
        calendario.append(fila)
    return calendario


# ------------------- CRUD Eventos -------------------

@cronograma_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_evento():
    """Crear un nuevo evento (solo coordinador/profesor)."""
    rol = session.get('rol')
    if rol not in ['profesor', 'coordinador']:
        flash('No tienes permisos para crear eventos.', 'error')
        return redirect(url_for('cronograma.listar_cronograma'))

    if request.method == 'POST':
        usuario_id = session.get('usuario_id')

        evento = Cronograma(
            titulo=request.form.get('titulo'),
            descripcion=request.form.get('descripcion'),
            fecha_evento=request.form.get('fecha'),
            tipo=request.form.get('tipo'),
            materia_id=request.form.get('materia_id') or None,
            curso_id=request.form.get('curso_id') or None,
            creado_por=usuario_id
        )
        evento.guardar()
        flash('Evento creado exitosamente.', 'success')
        return redirect(url_for('cronograma.listar_cronograma'))

    return render_template(
        'aplicacion/formularios/crear_evento.html',
        page_title='Crear Evento',
        active_page='cronograma',
        materias=Materia.obtener_todas(),
        cursos=Curso.obtener_todos(),
        evento=None
    )


@cronograma_bp.route('/<int:evento_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_evento(evento_id):
    """Editar un evento existente (solo coordinador/profesor)."""
    rol = session.get('rol')
    if rol not in ['profesor', 'coordinador']:
        flash('No tienes permisos para editar eventos.', 'error')
        return redirect(url_for('cronograma.listar_cronograma'))

    evento = Cronograma.obtener_por_id(evento_id)
    if not evento:
        flash('Evento no encontrado.', 'error')
        return redirect(url_for('cronograma.listar_cronograma'))

    if request.method == 'POST':
        evento.titulo = request.form.get('titulo')
        evento.descripcion = request.form.get('descripcion')
        evento.fecha_evento = request.form.get('fecha')
        evento.tipo = request.form.get('tipo')
        evento.materia_id = request.form.get('materia_id') or None
        evento.curso_id = request.form.get('curso_id') or None
        evento.actualizar()

        flash('Evento actualizado.', 'success')
        return redirect(url_for('cronograma.listar_cronograma'))

    return render_template(
        'aplicacion/formularios/crear_evento.html',
        page_title='Editar Evento',
        active_page='cronograma',
        materias=Materia.obtener_todas(),
        cursos=Curso.obtener_todos(),
        evento=evento
    )


@cronograma_bp.route('/<int:evento_id>/eliminar', methods=['GET','POST'])
@login_required
@eliminacion_segura
def eliminar_evento(evento_id):
    """Eliminar un evento (solo coordinador/profesor)."""
    rol = session.get('rol')
    if rol not in ['profesor', 'coordinador']:
        flash('No tienes permisos para eliminar eventos.', 'error')
        return redirect(url_for('cronograma.listar_cronograma'))

    evento = Cronograma.obtener_por_id(evento_id)
    if not evento:
        flash('Evento no encontrado.', 'error')
        return redirect(url_for('cronograma.listar_cronograma'))

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('evento', evento_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de evento',
            entidad_nombre=evento.titulo,
            entidad_id=evento_id,
            dependencias=dependencias,
            volver_url=request.referrer or url_for('cronograma.listar_cronograma')
        )

    evento.eliminar()
    flash('Evento eliminado.', 'success')
    return redirect(url_for('cronograma.listar_cronograma'))


# ------------------- Listado principal -------------------

@cronograma_bp.route('/')
@modulo_requerido('cronograma')
def listar_cronograma():
    """Muestra el calendario del mes actual con los eventos reales de la BD."""
    hoy = date.today()
    usuario_id = session.get('usuario_id')
    rol = session.get('rol', 'estudiante')
    eventos = Cronograma.obtener_todos(profesor_id=usuario_id if rol == 'profesor' else None)

    calendario = _construir_calendario_mes(hoy.year, hoy.month, eventos)

    proximos_eventos = []
    for ev in eventos:
        fecha_ev = ev.fecha_evento
        if hasattr(fecha_ev, 'date'):
            fecha_ev = fecha_ev.date()
        if fecha_ev and fecha_ev >= hoy:
            proximos_eventos.append(f"{ev.titulo} — {fecha_ev.strftime('%d/%m/%Y')}")
    proximos_eventos = proximos_eventos[:6]

    # dentro de listar_cronograma
    timeline = []
    for ev in eventos:
        fecha_ev = ev.fecha_evento
        if hasattr(fecha_ev, 'date'):
            fecha_ev = fecha_ev.date()
        semana_titulo = f"Semana {fecha_ev.isocalendar()[1]} — {fecha_ev.strftime('%d %B %Y')}"
        timeline.append({
            'titulo': semana_titulo,
            'eventos': [{
                'id': ev.id,
                'dia': fecha_ev.day,
                'mes': fecha_ev.strftime('%b'),
                'titulo': ev.titulo,
                'descripcion': ev.descripcion,
                'materia': ev.materia_nombre if ev.materia_nombre else None,
                'curso': getattr(ev, 'curso_codigo', None),
                'nivel': getattr(ev, 'nivel', None),
                'tipo': getattr(ev, 'tipo', None)
            }]
        })

    contexto = {
        'tareas_pendientes': 0,
        'eventos_proximos': len(proximos_eventos),
        'tareas_completadas': 0,
        'mensajes_nuevos': Mensaje.contar_no_leidos(usuario_id),
        'grupos': 0,
        'entregas_pendientes': 0,
        'estudiantes_activos': 0,
        'profesores': 0,
    }

    if rol == 'estudiante':
        tareas = Tarea.obtener_para_estudiante(usuario_id)
        contexto['tareas_pendientes'] = len(tareas)
        contexto['tareas_completadas'] = Entrega.contar_completadas_estudiante(usuario_id)

    elif rol == 'profesor':
        contexto['tareas_pendientes'] = len(Tarea.obtener_todas(profesor_id=usuario_id))
        grupos = Grupo.obtener_todos()
        contexto['grupos'] = sum(1 for g in grupos if g.creado_por == usuario_id)

    elif rol == 'coordinador':
        usuarios = Usuario.obtener_todos()
        contexto['estudiantes_activos'] = sum(1 for u in usuarios if u.rol == 'estudiante' and u.activo)
        contexto['profesores'] = sum(1 for u in usuarios if u.rol == 'profesor')

    return render_template(
        'aplicacion/cronograma.html',
        page_title='Cronograma',
        active_page='cronograma',
        calendario=calendario,
        proximos_eventos=proximos_eventos,
        eventos=eventos,
        timeline=timeline,
        **contexto
    )
