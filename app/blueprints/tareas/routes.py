"""
Rutas del blueprint de Tareas.

Cada tarea pertenece a una asignación académica puntual (curso_materia_id
= MATERIA + CURSO + PROFESOR). Reglas de rol:
- estudiante: solo ve y entrega tareas de SU curso.
- profesor: crea/edita/elimina y revisa/califica SOLO sus propias
  asignaciones académicas (su materia en su curso), nunca las de otro
  profesor aunque sea la misma materia.
- coordinador: puede todo, sobre cualquier tarea.
"""

import os
import uuid

from flask import (render_template, request, redirect, url_for, session, flash, current_app, send_from_directory, abort)
from werkzeug.utils import secure_filename
from datetime import date
from app.blueprints import tareas_bp
from app.models import Tarea, Entrega, Curso
from app.decorators import login_required, roles_permitidos, modulo_requerido, accion_requerida, eliminacion_segura


def _extension_permitida(nombre_archivo: str) -> bool:
    return '.' in nombre_archivo and \
        nombre_archivo.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def _puede_gestionar(tarea) -> bool:
    """Coordinador puede gestionar cualquier tarea; profesor solo las de su
    propia asignación académica (curso_materia.profesor_id), no basta con
    haberla creado si después le reasignaron la materia a otro."""
    rol = session.get('rol')
    if rol == 'coordinador':
        return True
    if rol == 'profesor':
        usuario_id = session.get('usuario_id')
        return tarea.creado_por == usuario_id or getattr(tarea, 'profesor_id', None) == usuario_id
    return False


def _asignaciones_del_profesor(profesor_id):
    """Paquete de materias que dicta un profesor, cada una con su curso
    (para el select de "crear tarea" y para acotar los filtros)."""
    from app.config_db import db
    consulta = """
        SELECT cm.id as curso_materia_id, m.nombre as materia_nombre,
               c.codigo as curso_codigo, c.id as curso_id
        FROM curso_materia cm
        JOIN materia m ON cm.materia_id = m.id
        JOIN curso c ON cm.curso_id = c.id
        WHERE cm.profesor_id = %s
        ORDER BY m.nombre, c.codigo
    """
    return db.ejecutar_consulta(consulta, (profesor_id,))


@tareas_bp.route('/')
@modulo_requerido('tareas')
def listar_tareas():
    """Lista tareas SEGÚN EL ROL: el estudiante solo ve las de su curso, el
    profesor solo las de sus propias asignaciones, el coordinador ve todas."""
    usuario_id = session.get('usuario_id')
    rol = session.get('rol', 'estudiante')

    if rol == 'estudiante':
        tareas = Tarea.obtener_para_estudiante(usuario_id)
    elif rol == 'profesor':
        tareas = Tarea.obtener_todas(profesor_id=usuario_id)
    else:
        tareas = Tarea.obtener_todas()

    hoy = date.today()
    total_tareas = len(tareas)
    tareas_proximas = sum(1 for t in tareas if t.fecha_limite and 0 <= (t.fecha_limite - hoy).days <= 3)
    tareas_vencidas = sum(1 for t in tareas if t.fecha_limite and t.fecha_limite < hoy)

    # paginación simple
    import math
    pagina = int(request.args.get('pagina', 1))
    por_pagina = 10
    total_paginas = max(1, math.ceil(total_tareas / por_pagina))
    if pagina < 1:
        pagina = 1
    if pagina > total_paginas:
        pagina = total_paginas
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    tareas_pagina = tareas[inicio:fin]

    for tarea in tareas_pagina:
        tarea.total_entregas = Entrega.contar_por_tarea(tarea.id)

    return render_template(
        'aplicacion/tareas.html',
        page_title='Tareas',
        active_page='tareas',
        tareas=tareas_pagina,
        rol=rol,
        usuario_id=usuario_id,
        total_tareas=total_tareas,
        tareas_proximas=tareas_proximas,
        tareas_vencidas=tareas_vencidas,
        pagina=pagina,
        total_paginas=total_paginas
    )


@tareas_bp.route('/crear', methods=['GET', 'POST'])
@roles_permitidos('profesor', 'coordinador')
@accion_requerida('tareas', 'crear')
def crear_tarea():
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')

    if request.method == 'POST':
        curso_materia_id = request.form.get('curso_materia_id')

        # Defensa real en backend: un profesor solo puede crear tareas sobre
        # SU PROPIA asignación académica, nunca sobre la de otro (aunque
        # arme el POST a mano apuntando a otro curso_materia_id).
        if rol == 'profesor':
            propias = {str(a['curso_materia_id']) for a in _asignaciones_del_profesor(usuario_id)}
            if curso_materia_id not in propias:
                flash('Solo podés crear tareas sobre tus propias asignaciones académicas.', 'error')
                return redirect(url_for('tareas.listar_tareas'))

        tarea = Tarea(
            titulo=request.form.get('titulo'),
            instrucciones=request.form.get('instrucciones'),
            fecha_limite=request.form.get('fecha_limite'),
            curso_materia_id=curso_materia_id,
            creado_por=usuario_id
        )
        tarea.guardar()
        flash('Tarea creada exitosamente.', 'success')
        return redirect(url_for('tareas.listar_tareas'))

    asignaciones = _asignaciones_del_profesor(usuario_id) if rol == 'profesor' else _todas_las_asignaciones()
    return render_template(
        'aplicacion/formularios/crear_tarea.html',
        page_title='Crear Tarea',
        active_page='tareas',
        asignaciones=asignaciones
    )


def _todas_las_asignaciones():
    """Para el coordinador: todas las asignaciones académicas del sistema."""
    from app.config_db import db
    consulta = """
        SELECT cm.id as curso_materia_id, m.nombre as materia_nombre,
               c.codigo as curso_codigo, c.id as curso_id, u.nombre as profesor_nombre
        FROM curso_materia cm
        JOIN materia m ON cm.materia_id = m.id
        JOIN curso c ON cm.curso_id = c.id
        LEFT JOIN usuario u ON cm.profesor_id = u.id
        ORDER BY m.nombre, c.codigo
    """
    return db.ejecutar_consulta(consulta)


@tareas_bp.route('/<int:tarea_id>/editar', methods=['GET', 'POST'])
@roles_permitidos('profesor', 'coordinador')
@accion_requerida('tareas', 'editar')
def editar_tarea(tarea_id):
    tarea = Tarea.obtener_por_id(tarea_id)
    if not tarea:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    if not _puede_gestionar(tarea):
        flash('Solo podés editar las tareas de tus propias asignaciones académicas.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    if request.method == 'POST':
        tarea.titulo = request.form.get('titulo')
        tarea.instrucciones = request.form.get('instrucciones')
        tarea.fecha_limite = request.form.get('fecha_limite')
        tarea.actualizar()
        flash('Tarea actualizada.', 'success')
        return redirect(url_for('tareas.listar_tareas'))

    return render_template(
        'aplicacion/formularios/crear_tarea.html',
        page_title='Editar Tarea',
        active_page='tareas',
        tarea=tarea
    )


@tareas_bp.route('/<int:tarea_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('profesor', 'coordinador')
@accion_requerida('tareas', 'eliminar')
@eliminacion_segura
def eliminar_tarea(tarea_id):
    tarea = Tarea.obtener_por_id(tarea_id)
    if not tarea:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    if not _puede_gestionar(tarea):
        flash('Solo podés eliminar las tareas de tus propias asignaciones académicas.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('tarea', tarea_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de tarea',
            entidad_nombre=tarea.titulo,
            entidad_id=tarea_id,
            dependencias=dependencias,
            volver_url=request.referrer or url_for('tareas.listar_tareas')
        )

    tarea.eliminar()
    flash('Tarea eliminada.', 'success')
    return redirect(url_for('tareas.listar_tareas'))


# ---------------------------------------------------------------
# Entrega de archivo por el estudiante
# ---------------------------------------------------------------

@tareas_bp.route('/<int:tarea_id>/entregar', methods=['GET', 'POST'])
@roles_permitidos('estudiante')
def entregar_tarea(tarea_id):
    """Pantalla donde un estudiante sube el archivo de su entrega. Verifica
    que la tarea realmente le corresponda a SU curso (nunca a otro)."""
    tarea = Tarea.obtener_por_id(tarea_id)
    if not tarea:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    estudiante_id = session.get('usuario_id')

    destinatarios = {d['id'] for d in Tarea.obtener_destinatarios(tarea_id)}
    if estudiante_id not in destinatarios:
        flash('Esta tarea no corresponde a tu curso.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    entrega_existente = Entrega.obtener_por_estudiante_y_tarea(tarea_id, estudiante_id)

    if request.method == 'POST':
        archivo = request.files.get('archivo')
        comentario = request.form.get('comentario')

        if not archivo or archivo.filename == '':
            flash('Tenés que seleccionar un archivo.', 'error')
            return redirect(url_for('tareas.entregar_tarea', tarea_id=tarea_id))

        if not _extension_permitida(archivo.filename):
            flash('Tipo de archivo no permitido. Usá PDF, Word, PowerPoint, Excel, imagen o ZIP.', 'error')
            return redirect(url_for('tareas.entregar_tarea', tarea_id=tarea_id))

        nombre_original = secure_filename(archivo.filename)
        extension = nombre_original.rsplit('.', 1)[1].lower()
        nombre_guardado = f"{uuid.uuid4().hex}.{extension}"
        archivo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_guardado))

        entrega = Entrega(
            tarea_id=tarea_id,
            estudiante_id=estudiante_id,
            archivo_url=nombre_guardado,
            archivo_nombre_original=nombre_original,
            comentario=comentario
        )
        entrega.guardar()
        flash('Tarea entregada correctamente.', 'success')
        return redirect(url_for('tareas.listar_tareas'))

    return render_template(
        'aplicacion/formularios/entregar_tareas.html',
        page_title='Entregar Tarea',
        active_page='tareas',
        tarea=tarea,
        entrega_existente=entrega_existente
    )


# ---------------------------------------------------------------
# Revision y valoracion por el profesor/coordinador
# ---------------------------------------------------------------

@tareas_bp.route('/<int:tarea_id>/revisar')
@roles_permitidos('profesor', 'coordinador')
def revisar_entregas(tarea_id):
    """Pantalla del profesor/coordinador: roster de estudiantes del curso
    de la tarea (nunca de otro) y sus entregas."""
    tarea = Tarea.obtener_por_id(tarea_id)
    if not tarea:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    if not _puede_gestionar(tarea):
        flash('Solo podés revisar las entregas de tus propias asignaciones académicas.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    roster = Entrega.obtener_estado_por_tarea(tarea_id)

    return render_template(
        'aplicacion/formularios/revisar_entregas.html',
        page_title='Revisar Entregas',
        active_page='tareas',
        tarea=tarea,
        roster=roster
    )


@tareas_bp.route('/entregas/<int:entrega_id>/calificar', methods=['POST'])
@roles_permitidos('profesor', 'coordinador')
@accion_requerida('tareas', 'calificar')
def calificar_entrega(entrega_id):
    """Guarda la nota y el comentario del profesor para una entrega puntual."""
    entrega_data = Entrega.obtener_por_id(entrega_id)
    if not entrega_data:
        flash('Entrega no encontrada.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    tarea = Tarea.obtener_por_id(entrega_data.tarea_id)
    if not tarea or not _puede_gestionar(tarea):
        flash('Solo podés calificar entregas de tus propias asignaciones académicas.', 'error')
        return redirect(url_for('tareas.listar_tareas'))

    nota = request.form.get('nota')
    comentario = request.form.get('comentario_profesor')
    entrega_data.calificar(nota, comentario)
    flash('Calificación guardada.', 'success')
    return redirect(url_for('tareas.revisar_entregas', tarea_id=entrega_data.tarea_id))


# ---------------------------------------------------------------
# Descarga protegida del archivo
# ---------------------------------------------------------------

@tareas_bp.route('/entregas/<int:entrega_id>/descargar')
@login_required
def descargar_entrega(entrega_id):
    """
    Descarga el archivo de una entrega.
    Permitido: el estudiante dueño de la entrega, o el profesor/coordinador
    responsable de esa asignación académica (no cualquier profesor puede
    bajar entregas ajenas, ni siquiera de la misma materia en otro curso).
    """
    entrega_data = Entrega.obtener_por_id(entrega_id)
    if not entrega_data or not entrega_data.archivo_url:
        abort(404)

    usuario_id = session.get('usuario_id')
    rol = session.get('rol')
    es_dueno = entrega_data.estudiante_id == usuario_id

    tarea = Tarea.obtener_por_id(entrega_data.tarea_id)
    es_revisor = tarea and _puede_gestionar(tarea) if rol in ('profesor', 'coordinador') else False

    if not (es_dueno or es_revisor):
        abort(403)

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        entrega_data.archivo_url,
        as_attachment=True,
        download_name=entrega_data.archivo_nombre_original or entrega_data.archivo_url
    )
