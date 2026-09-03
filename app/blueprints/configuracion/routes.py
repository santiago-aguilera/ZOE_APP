"""
Rutas del blueprint de Configuracion.
Panel de administracion: usuarios, materias, grupos y cohortes.
La Matrícula BI tiene su propio módulo dedicado (ver blueprint 'matricula').
"""

from flask import render_template, request, redirect, url_for, flash

from app.blueprints import configuracion_bp
from app.models import Usuario, Materia, Grupo, Cohorte
from app.decorators import roles_permitidos, accion_requerida


@configuracion_bp.route('/')
@roles_permitidos('coordinador')
def configuracion():
    """Panel de administracion con datos reales de las secciones."""
    usuarios = Usuario.obtener_todos()
    cohortes = Cohorte.obtener_todos()

    return render_template(
        'aplicacion/config/configuracion.html',
        page_title='Configuración',
        active_page='configuracion',
        usuarios=usuarios,
        materias=Materia.obtener_todas(),
        grupos=Grupo.obtener_todos(),
        cohortes=cohortes,
        profesores=[u for u in usuarios if u.rol == 'profesor'],
        estudiantes=[u for u in usuarios if u.rol == 'estudiante'],
        grupos_todos=Grupo.obtener_todos(),
        asignaciones_estudiante_grupo=Grupo.obtener_asignaciones()
    )


@configuracion_bp.route('/cohortes/crear', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
def form_crear_cohorte():
    if request.method == 'POST':
        cohorte = Cohorte(
            nombre=request.form.get('nombre'),
            fecha_inicio=request.form.get('fecha_inicio'),
            fecha_fin=request.form.get('fecha_fin')
        )
        cohorte.guardar()
        flash('Cohorte académica creada exitosamente.', 'success')
        return redirect(url_for('configuracion.configuracion'))

    return render_template(
        'aplicacion/formularios/editar_cohorte.html',
        page_title='Crear Cohorte',
        active_page='configuracion'
    )


@configuracion_bp.route('/cohortes/<int:cohorte_id>/editar', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
def editar_cohorte(cohorte_id):
    cohorte = Cohorte.obtener_por_id(cohorte_id)
    if not cohorte:
        flash('Cohorte no encontrada.', 'error')
        return redirect(url_for('configuracion.configuracion') + '#cohortes')

    if request.method == 'POST':
        cohorte.nombre = request.form.get('nombre')
        cohorte.fecha_inicio = request.form.get('fecha_inicio')
        cohorte.fecha_fin = request.form.get('fecha_fin')
        cohorte.activo = request.form.get('activo') == 'on'
        cohorte.actualizar()
        flash('Cohorte actualizada.', 'success')
        return redirect(url_for('configuracion.configuracion') + '#cohortes')

    return render_template(
        'aplicacion/formularios/editar_cohorte.html',
        page_title='Editar Cohorte',
        active_page='configuracion',
        cohorte=cohorte
    )


@configuracion_bp.route('/cohortes/<int:cohorte_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('coordinador')
def eliminar_cohorte(cohorte_id):
    cohorte = Cohorte.obtener_por_id(cohorte_id)
    if not cohorte:
        flash('Cohorte no encontrada.', 'error')
        return redirect(url_for('configuracion.configuracion') + '#cohortes')

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('cohorte', cohorte_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de cohorte',
            entidad_nombre=cohorte.nombre,
            entidad_id=cohorte_id,
            dependencias=dependencias,
            volver_url=request.referrer or (url_for('configuracion.configuracion') + '#cohortes')
        )

    cohorte.eliminar()
    flash('Cohorte eliminada.', 'success')
    return redirect(url_for('configuracion.configuracion') + '#cohortes' )


# ---------------------------------------------------------------
# Asignaciones: estudiante <-> grupo
# ---------------------------------------------------------------

@configuracion_bp.route('/asignaciones/estudiante-grupo', methods=['POST'])
@roles_permitidos('coordinador')
@accion_requerida('grupos', 'asignar')
def asignar_estudiante_grupo():
    estudiante_id = request.form.get('estudiante_id')
    grupo_id = request.form.get('grupo_id')
    if estudiante_id and grupo_id:
        if Grupo.inscribir_estudiante(grupo_id, estudiante_id):
            flash('Estudiante inscrito en el grupo.', 'success')
        else:
            flash('No se pudo inscribir: el estudiante no existe, o el grupo está restringido a un curso/cohorte específico y no pertenece a ese contexto.', 'error')
    else:
        flash('Seleccioná un estudiante y un grupo.', 'error')
    return redirect(url_for('configuracion.configuracion') + '#asignaciones')


@configuracion_bp.route('/asignaciones/estudiante-grupo/<int:asignacion_id>/quitar', methods=['POST'])
@roles_permitidos('coordinador')
@accion_requerida('grupos', 'asignar')
def quitar_estudiante_grupo(asignacion_id):
    Grupo.quitar_estudiante(asignacion_id)
    flash('Inscripción eliminada.', 'success')
    return redirect(url_for('configuracion.configuracion') + '#asignaciones')
