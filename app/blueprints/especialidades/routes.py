"""
Rutas del blueprint de Especialidades.

Programación de Software, Diseño Multimedia, Ambiental, Administración de
Empresas. Funciona como un curso (agrupa estudiantes dentro de una cohorte)
pero con un solo profesor asignado. Se auto-generan las 4 al crear la
cohorte (ver Cohorte.guardar() en models.py).
"""

from flask import render_template, request, redirect, url_for, flash

from app.blueprints import especialidades_bp
from app.models import Especialidad, Cohorte, Usuario
from app.decorators import login_required, roles_permitidos, modulo_requerido, accion_requerida


@especialidades_bp.route('/')
@modulo_requerido('especialidades')
def listar_especialidades():
    """Lista todas las especialidades, opcionalmente filtradas por cohorte."""
    cohorte_id = request.args.get('cohorte_id', type=int)
    especialidades = Especialidad.obtener_todas(cohorte_id=cohorte_id)
    cohortes = Cohorte.obtener_todos()
    return render_template(
        'aplicacion/especialidades/especialidades.html',
        page_title='Especialidades',
        active_page='especialidades',
        especialidades=especialidades,
        cohortes=cohortes,
        filtro_cohorte=cohorte_id
    )


@especialidades_bp.route('/<int:especialidad_id>')
@login_required
def ver_especialidad(especialidad_id):
    """Detalle de una especialidad: estudiantes y profesor asignado."""
    especialidad = Especialidad.obtener_por_id(especialidad_id)
    if not especialidad:
        flash('Especialidad no encontrada.', 'error')
        return redirect(url_for('especialidades.listar_especialidades'))

    estudiantes = Especialidad.obtener_estudiantes(especialidad_id)
    todos_usuarios = Usuario.obtener_todos()
    estudiantes_ids_actuales = {e['usuario_id'] for e in estudiantes}

    estudiantes_disponibles = [
        u for u in todos_usuarios
        if u.rol == 'estudiante' and u.id not in estudiantes_ids_actuales
    ]
    profesores = [u for u in todos_usuarios if u.rol == 'profesor']

    return render_template(
        'aplicacion/especialidades/ver_especialidad.html',
        page_title=especialidad.nombre,
        active_page='especialidades',
        especialidad=especialidad,
        estudiantes=estudiantes,
        estudiantes_disponibles=estudiantes_disponibles,
        profesores=profesores
    )


@especialidades_bp.route('/<int:especialidad_id>/estudiantes/agregar', methods=['POST'])
@roles_permitidos('coordinador')
def agregar_estudiante(especialidad_id):
    """Inscribe un estudiante en la especialidad."""
    estudiante_id = request.form.get('estudiante_id')
    if estudiante_id:
        Especialidad.inscribir_estudiante(especialidad_id, estudiante_id)
        flash('Estudiante inscrito en la especialidad.', 'success')
    return redirect(url_for('especialidades.ver_especialidad', especialidad_id=especialidad_id))


@especialidades_bp.route('/<int:especialidad_id>/estudiantes/<int:asignacion_id>/quitar', methods=['POST'])
@roles_permitidos('coordinador')
def quitar_estudiante(especialidad_id, asignacion_id):
    """Quita a un estudiante de la especialidad."""
    Especialidad.quitar_estudiante(asignacion_id)
    flash('Estudiante removido de la especialidad.', 'success')
    return redirect(url_for('especialidades.ver_especialidad', especialidad_id=especialidad_id))


@especialidades_bp.route('/<int:especialidad_id>/profesor', methods=['POST'])
@roles_permitidos('coordinador')
@accion_requerida('especialidades', 'asignar')
def asignar_profesor(especialidad_id):
    """Asigna o cambia el profesor de la especialidad."""
    profesor_id = request.form.get('profesor_id') or None
    Especialidad.asignar_profesor(especialidad_id, profesor_id)
    flash('Profesor asignado.', 'success')
    return redirect(url_for('especialidades.ver_especialidad', especialidad_id=especialidad_id))
