"""
Rutas del blueprint de Matrícula BI.

usuario.estado_matricula es la ÚNICA fuente de verdad del estado ACTUAL de
un estudiante (sin historial: este módulo no lleva un log de cambios).

Herramienta administrativa institucional: estadísticas, filtros
combinables y cambio de estado.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import matricula_bp
from app.models import Usuario, Cohorte, Curso, ESTADOS_MATRICULA, ETIQUETAS_ESTADO_MATRICULA
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
