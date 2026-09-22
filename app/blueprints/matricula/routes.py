"""
Rutas del blueprint de Matrícula BI.

usuario.estado_matricula es la ÚNICA fuente de verdad del estado ACTUAL de
un estudiante (sin historial: este módulo no lleva un log de cambios).

Herramienta administrativa institucional: estadísticas, filtros
combinables y cambio de estado.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import matricula_bp
from app.models import (Usuario, Cohorte, Curso, Materia, NotaPrevista, InformeFinal,
                         SeleccionMatriculado, ESTADOS_MATRICULA, ETIQUETAS_ESTADO_MATRICULA)
from app.decorators import roles_permitidos, accion_requerida, modulo_requerido


@matricula_bp.route('/')
@modulo_requerido('matricula')
def inicio():
    """Panel administrativo: estadísticas + listado filtrable de estudiantes."""
    cohorte_id = request.args.get('cohorte_id', type=int)
    curso_id = request.args.get('curso_id', type=int)
    estado = request.args.get('estado_matricula') or None
    texto = request.args.get('q', '').strip()

    estudiantes = Usuario.obtener_todos(cohorte_id=cohorte_id, curso_id=curso_id,
                                         estado_matricula=estado, rol='estudiante')
    if texto:
        texto_lower = texto.lower()
        estudiantes = [e for e in estudiantes if texto_lower in (e.nombre or '').lower()
                       or texto_lower in (e.correo or '').lower()]

    cursos_por_id = {c.id: c for c in Curso.obtener_todos()}
    cohortes_por_id = {c.id: c for c in Cohorte.obtener_todos()}
    for e in estudiantes:
        e.curso_obj = cursos_por_id.get(e.curso_id)
        e.cohorte_obj = cohortes_por_id.get(e.cohorte_id)

    return render_template(
        'aplicacion/matricula/matricula.html',
        page_title='Matrícula BI',
        active_page='matricula',
        estudiantes=estudiantes,
        estadisticas=Usuario.obtener_estadisticas_matricula(cohorte_id=cohorte_id),
        cohortes=Cohorte.obtener_todos(),
        cursos=Curso.obtener_todos(),
        estados_matricula=ESTADOS_MATRICULA,
        etiquetas_estado=ETIQUETAS_ESTADO_MATRICULA,
        filtro_cohorte=cohorte_id,
        filtro_curso=curso_id,
        filtro_estado=estado,
        filtro_texto=texto
    )


@matricula_bp.route('/<int:usuario_id>/cambiar-estado', methods=['POST'])
@roles_permitidos('coordinador')
@accion_requerida('matricula', 'cambiar_estado')
def cambiar_estado(usuario_id):
    """Cambia el estado ACTUAL de matrícula BI de un estudiante
    (usuario.estado_matricula es la única fuente de verdad, sin historial)."""
    estudiante = Usuario.obtener_por_id(usuario_id)
    if not estudiante or estudiante.rol != 'estudiante':
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('matricula.inicio'))

    nuevo_estado = request.form.get('estado_matricula')
    if nuevo_estado not in ESTADOS_MATRICULA:
        flash('Estado de matrícula inválido.', 'error')
        return redirect(request.referrer or url_for('matricula.inicio'))

    estudiante.cambiar_estado_matricula(nuevo_estado)
    flash(f"{estudiante.nombre} ahora está en estado {ETIQUETAS_ESTADO_MATRICULA.get(nuevo_estado, nuevo_estado)}.", 'success')
    return redirect(request.referrer or url_for('matricula.inicio'))


@matricula_bp.route('/<int:usuario_id>/repite-anio', methods=['POST'])
@roles_permitidos('coordinador')
def repite_anio(usuario_id):
    """El estudiante no pasó el año: lo mueve de su cohorte actual a la
    misma sección de décimo de la cohorte siguiente, y deja registro en
    estudiante_repitencia (Usuario.repetir_anio)."""
    try:
        resultado = Usuario.repetir_anio(usuario_id, session.get('usuario_id'))
        flash(f"Estudiante pasado a la cohorte \"{resultado['cohorte_destino']}\", curso {resultado['curso_destino']}.", 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(request.referrer or url_for('matricula.inicio'))


# ---------------------------------------------------------------
# Nota Prevista: solo materias normales, la da el profesor una vez al
# cierre de décimo / inicio de once. Es la nota decisiva para la selección.
# ---------------------------------------------------------------

@matricula_bp.route('/<int:usuario_id>/nota-prevista', methods=['POST'])
@roles_permitidos('coordinador', 'profesor')
@accion_requerida('nota_prevista', 'crear')
def guardar_nota_prevista(usuario_id):
    materia_id = request.form.get('materia_id', type=int)
    valor = request.form.get('valor', type=float)
    materia = Materia.obtener_por_id(materia_id) if materia_id else None

    if not materia or materia.tipo != 'normal':
        flash('La nota prevista solo aplica a materias normales.', 'error')
        return redirect(request.referrer or url_for('matricula.inicio'))
    if valor is None or valor < 1 or valor > 7:
        flash('La nota prevista debe estar entre 1 y 7.', 'error')
        return redirect(request.referrer or url_for('matricula.inicio'))

    nota = NotaPrevista(usuario_id=usuario_id, materia_id=materia_id,
                         profesor_id=session.get('usuario_id'), valor=valor)
    nota.guardar_o_actualizar()
    flash(f'Nota prevista de {materia.nombre} registrada.', 'success')
    return redirect(request.referrer or url_for('matricula.inicio'))


# ---------------------------------------------------------------
# Informe Final: réplica digital del informe que hoy diligencian los
# profesores a mano. "Alcanzó" se prellena solo; la Recomendación siempre
# la escribe el profesor.
# ---------------------------------------------------------------

@matricula_bp.route('/<int:usuario_id>/informe/<int:cohorte_id>')
@modulo_requerido('informe_final')
def ver_informe_final(usuario_id, cohorte_id):
    estudiante = Usuario.obtener_por_id(usuario_id)
    if not estudiante:
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('matricula.inicio'))

    informe = InformeFinal.obtener_por_estudiante_cohorte(usuario_id, cohorte_id)
    notas_previstas = {n['materia_id']: n for n in NotaPrevista.obtener_por_estudiante(usuario_id)}
    return render_template(
        'aplicacion/matricula/informe_final.html',
        page_title=f'Informe final — {estudiante.nombre}',
        active_page='matricula',
        estudiante=estudiante,
        cohorte_id=cohorte_id,
        informe=informe,
        materias_normales=Materia.obtener_todas_por_tipo('normal'),
        notas_previstas=notas_previstas,
        nota_prevista_promedio=NotaPrevista.promedio_por_estudiante(usuario_id)
    )


@matricula_bp.route('/<int:usuario_id>/informe/<int:cohorte_id>/generar', methods=['POST'])
@roles_permitidos('coordinador', 'profesor')
@accion_requerida('informe_final', 'editar')
def generar_informe_final(usuario_id, cohorte_id):
    """Genera (o regenera) el informe: una fila por descriptor de la
    cohorte, con 'Alcanzó' prellenado según la evidencia ya subida."""
    InformeFinal.generar_para_estudiante(usuario_id, cohorte_id, session.get('usuario_id'))
    flash('Informe final generado. Revisá "Alcanzó" y escribí la recomendación de cada componente.', 'success')
    return redirect(url_for('matricula.ver_informe_final', usuario_id=usuario_id, cohorte_id=cohorte_id))


@matricula_bp.route('/informe/detalle/<int:detalle_id>/guardar', methods=['POST'])
@roles_permitidos('coordinador', 'profesor')
@accion_requerida('informe_final', 'editar')
def guardar_detalle_informe(detalle_id):
    """El profesor ajusta 'Alcanzó' (prellenado por el sistema) y escribe
    la Recomendación a mano."""
    alcanzo = request.form.get('alcanzo') == 'on'
    recomendacion = request.form.get('recomendacion')
    InformeFinal.actualizar_detalle(detalle_id, alcanzo, recomendacion, session.get('usuario_id'))
    flash('Componente del informe actualizado.', 'success')
    return redirect(request.referrer or url_for('matricula.inicio'))


# ---------------------------------------------------------------
# Selección de matriculados: décimo -> POP. Insumos: informe final +
# nota prevista + una métrica futura (placeholder por ahora).
# ---------------------------------------------------------------

@matricula_bp.route('/seleccion/<int:cohorte_id>')
@modulo_requerido('matricula')
@roles_permitidos('coordinador')
def ver_seleccion(cohorte_id):
    return render_template(
        'aplicacion/matricula/seleccion.html',
        page_title='Selección de matriculados',
        active_page='matricula',
        cohorte_id=cohorte_id,
        seleccion=SeleccionMatriculado.obtener_por_cohorte(cohorte_id),
        estudiantes=Usuario.obtener_todos(cohorte_id=cohorte_id, rol='estudiante')
    )


@matricula_bp.route('/seleccion/<int:cohorte_id>/decidir', methods=['POST'])
@roles_permitidos('coordinador')
def decidir_seleccion(cohorte_id):
    usuario_id = request.form.get('usuario_id', type=int)
    seleccionado = request.form.get('seleccionado') == 'on'
    informe = InformeFinal.obtener_por_estudiante_cohorte(usuario_id, cohorte_id)

    decision = SeleccionMatriculado(
        usuario_id=usuario_id,
        cohorte_id=cohorte_id,
        informe_final_id=informe['id'] if informe else None,
        seleccionado=seleccionado
    )
    decision.guardar_o_actualizar()
    flash('Decisión de selección guardada.', 'success')
    return redirect(url_for('matricula.ver_seleccion', cohorte_id=cohorte_id))
