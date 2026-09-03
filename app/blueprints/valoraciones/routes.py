"""
Rutas del blueprint de Valoraciones.
Libro de notas por actividad valorativa, configurable por el profesor.

Reglas de rol:
- coordinador: ve y gestiona todas las materias.
- profesor: ve y gestiona SOLO las materias que dicta.
- estudiante: ve solo su propio boletín (mis-notas).
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import valoraciones_bp
from app.models import Materia, ActividadValorativa, ValoracionActividad, Usuario, ESCALA_VALORATIVA, VALOR_ORDINAL
from app.decorators import roles_permitidos, modulo_requerido, eliminacion_segura


def _materias_del_profesor():
    """Materias visibles para el profesor logueado (o todas, si es coordinador)."""
    if session.get('rol') == 'coordinador':
        return Materia.obtener_todas()
    ids = Materia.obtener_ids_por_profesor(session.get('usuario_id'))
    return [m for m in Materia.obtener_todas() if m.id in ids]


@valoraciones_bp.route('/')
@modulo_requerido('valoraciones')
@roles_permitidos('profesor', 'coordinador')
def listar_materias():
    """Lista las materias que el profesor puede calificar (o todas, si es coordinador)."""
    return render_template(
        'aplicacion/valoraciones/listar_materias.html',
        page_title='Valoraciones',
        active_page='valoraciones',
        materias=_materias_del_profesor()
    )


@valoraciones_bp.route('/materia/<int:materia_id>')
@roles_permitidos('profesor', 'coordinador')
def ver_materia(materia_id):
    """Libro de notas de una materia: matriz de actividades x estudiantes + boletín."""
    materia = Materia.obtener_por_id(materia_id)
    if not materia:
        flash('Materia no encontrada.', 'error')
        return redirect(url_for('valoraciones.listar_materias'))

    if session.get('rol') == 'profesor' and materia_id not in Materia.obtener_ids_por_profesor(session.get('usuario_id')):
        flash('Esa materia no está asignada a vos.', 'error')
        return redirect(url_for('valoraciones.listar_materias'))

    actividades = ActividadValorativa.obtener_por_materia(materia_id)
    estudiantes_raw = [r for r in _obtener_estudiantes_materia(materia_id)]
    valores = ValoracionActividad.obtener_notas_materia(materia_id)
    boletin = ValoracionActividad.obtener_boletin(materia_id)
    suma_porcentajes = ActividadValorativa.suma_porcentajes(materia_id)

    return render_template(
        'aplicacion/valoraciones/ver_materia.html',
        page_title=f'Valoraciones — {materia.nombre}',
        active_page='valoraciones',
        materia=materia,
        actividades=actividades,
        estudiantes=estudiantes_raw,
        valores=valores,
        escala=ESCALA_VALORATIVA,
        boletin=boletin,
        suma_porcentajes=suma_porcentajes
    )


def _obtener_estudiantes_materia(materia_id):
    """Lista de {id, nombre} de los estudiantes inscritos en una materia."""
    from app.config_db import db
    consulta = """
        SELECT DISTINCT u.id, u.nombre FROM curso_materia cm
        JOIN usuario u ON u.curso_id = cm.curso_id AND u.rol = 'estudiante'
        WHERE cm.materia_id = %s
        ORDER BY u.nombre
    """
    return db.ejecutar_consulta(consulta, (materia_id,))


@valoraciones_bp.route('/materia/<int:materia_id>/actividad/crear', methods=['POST'])
@roles_permitidos('profesor', 'coordinador')
def crear_actividad(materia_id):
    """Agrega una actividad valorativa nueva a la materia."""
    actividad = ActividadValorativa(
        materia_id=materia_id,
        nombre=request.form.get('nombre'),
        tipo=request.form.get('tipo'),
        porcentaje=request.form.get('porcentaje') or 0,
        fecha=request.form.get('fecha') or None,
        creado_por=session.get('usuario_id')
    )
    actividad.guardar()
    flash('Actividad agregada.', 'success')
    return redirect(url_for('valoraciones.ver_materia', materia_id=materia_id))


@valoraciones_bp.route('/actividad/<int:actividad_id>/editar', methods=['GET', 'POST'])
@roles_permitidos('profesor', 'coordinador')
def editar_actividad(actividad_id):
    """Edita nombre/tipo/porcentaje/fecha de una actividad existente."""
    actividad = ActividadValorativa.obtener_por_id(actividad_id)
    if not actividad:
        flash('Actividad no encontrada.', 'error')
        return redirect(url_for('valoraciones.listar_materias'))

    if session.get('rol') == 'profesor' and actividad.materia_id not in Materia.obtener_ids_por_profesor(session.get('usuario_id')):
        flash('Esa materia no está asignada a vos.', 'error')
        return redirect(url_for('valoraciones.listar_materias'))

    if request.method == 'POST':
        actividad.nombre = request.form.get('nombre')
        actividad.tipo = request.form.get('tipo')
        actividad.porcentaje = request.form.get('porcentaje') or 0
        actividad.fecha = request.form.get('fecha') or None
        actividad.actualizar()
        flash('Actividad actualizada.', 'success')
        return redirect(url_for('valoraciones.ver_materia', materia_id=actividad.materia_id))

    return render_template(
        'aplicacion/valoraciones/editar_actividad.html',
        page_title='Editar Actividad',
        active_page='valoraciones',
        actividad=actividad
    )


@valoraciones_bp.route('/actividad/<int:actividad_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('profesor', 'coordinador')
@eliminacion_segura
def eliminar_actividad(actividad_id):
    """Elimina una actividad (y sus notas cargadas, en cascada)."""
    actividad = ActividadValorativa.obtener_por_id(actividad_id)
    if not actividad:
        flash('Actividad no encontrada.', 'error')
        return redirect(url_for('valoraciones.listar_materias'))

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('actividad_valorativa', actividad_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de actividad',
            entidad_nombre=actividad.nombre,
            entidad_id=actividad_id,
            dependencias=dependencias,
            volver_url=request.referrer or url_for('valoraciones.ver_materia', materia_id=actividad.materia_id)
        )

    materia_id = actividad.materia_id
    actividad.eliminar()
    flash('Actividad eliminada.', 'success')
    return redirect(url_for('valoraciones.ver_materia', materia_id=materia_id))


@valoraciones_bp.route('/materia/<int:materia_id>/guardar-notas', methods=['POST'])
@roles_permitidos('profesor', 'coordinador')
def guardar_notas(materia_id):
    """Guarda todas las valoraciones de la matriz de una sola vez (campos valor_<actividad>_<estudiante>)."""
    for campo, valor in request.form.items():
        if not campo.startswith('valor_') or valor == '' or valor not in ESCALA_VALORATIVA:
            continue
        _, actividad_id, estudiante_id = campo.split('_')
        valoracion = ValoracionActividad(
            actividad_id=int(actividad_id),
            estudiante_id=int(estudiante_id),
            valor=valor
        )
        valoracion.guardar()

    flash('Valoraciones guardadas.', 'success')
    return redirect(url_for('valoraciones.ver_materia', materia_id=materia_id))


@valoraciones_bp.route('/materia/<int:materia_id>/valoracion-minima', methods=['POST'])
@roles_permitidos('profesor', 'coordinador')
def actualizar_valoracion_minima(materia_id):
    """Actualiza la valoración mínima de aprobación de una materia."""
    materia = Materia.obtener_por_id(materia_id)
    if not materia:
        flash('Materia no encontrada.', 'error')
        return redirect(url_for('valoraciones.listar_materias'))

    nueva_valoracion_minima = request.form.get('valoracion_minima_aprobatoria')
    if nueva_valoracion_minima not in ESCALA_VALORATIVA:
        flash('La valoración mínima tiene que ser Bajo, Básico, Alto o Superior.', 'error')
        return redirect(url_for('valoraciones.ver_materia', materia_id=materia_id))

    materia.actualizar_valoracion_minima(nueva_valoracion_minima)
    flash('Valoración mínima de aprobación actualizada.', 'success')
    return redirect(url_for('valoraciones.ver_materia', materia_id=materia_id))


# ---------------------------------------------------------------
# Vista del estudiante
# ---------------------------------------------------------------

@valoraciones_bp.route('/mis-notas')
@modulo_requerido('valoraciones')
@roles_permitidos('estudiante')
def mis_notas():
    """Boletín del estudiante en cada una de sus materias inscritas."""
    estudiante_id = session.get('usuario_id')
    materias = Usuario.obtener_materias(estudiante_id)

    resumen = []
    for materia in materias:
        boletin = ValoracionActividad.obtener_boletin(materia['id'])
        mi_fila = next((b for b in boletin if b['estudiante_id'] == estudiante_id), None)
        if mi_fila:
            resumen.append({'materia_id': materia['id'], 'materia_nombre': materia['nombre'], **mi_fila})

    return render_template(
        'aplicacion/valoraciones/mis_notas.html',
        page_title='Mis Valoraciones',
        active_page='valoraciones',
        resumen=resumen
    )


@valoraciones_bp.route('/mis-notas/<int:materia_id>')
@roles_permitidos('estudiante')
def mi_detalle_materia(materia_id):
    """Desglose actividad por actividad de una materia puntual, para el estudiante."""
    estudiante_id = session.get('usuario_id')
    materia = Materia.obtener_por_id(materia_id)
    if not materia:
        flash('Materia no encontrada.', 'error')
        return redirect(url_for('valoraciones.mis_notas'))

    detalle = ValoracionActividad.obtener_detalle_estudiante(materia_id, estudiante_id)

    return render_template(
        'aplicacion/valoraciones/mi_detalle_materia.html',
        page_title=f'Mis notas — {materia.nombre}',
        active_page='valoraciones',
        materia=materia,
        detalle=detalle,
        valor_ordinal=VALOR_ORDINAL
    )