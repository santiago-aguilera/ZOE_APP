"""
Rutas del blueprint de Materias.
Catálogo reutilizable de materias, independiente de cohorte y curso.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import materias_bp
from app.models import Materia
from app.decorators import login_required, roles_permitidos, modulo_requerido, accion_requerida


@materias_bp.route('/')
@modulo_requerido('materias')
def listar_materias():
    """Lista todas las materias del catálogo."""
    materias = Materia.obtener_todas()
    return render_template(
        'aplicacion/materias.html',
        page_title='Materias',
        active_page='materias',
        materias=materias,
        pagina=1,
        total_paginas=1,
        total_materias=len(materias)
    )


@materias_bp.route('/<int:materia_id>')
@modulo_requerido('materias')
def ver_materia(materia_id):
    """Detalle de una materia: en qué cursos se dicta y con qué profesor."""
    materia = Materia.obtener_por_id(materia_id)
    if not materia:
        flash('Materia no encontrada.', 'error')
        return redirect(url_for('materias.listar_materias'))

    return render_template(
        'aplicacion/materias/ver_materia.html',
        page_title=materia.nombre,
        active_page='materias',
        materia=materia,
        asignaciones=Materia.obtener_asignaciones(materia_id)
    )


@materias_bp.route('/crear', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
@accion_requerida('materias', 'crear')
def form_crear_materia():
    if request.method == 'POST':
        materia = Materia(
            nombre=request.form.get('nombre'),
            descripcion=request.form.get('descripcion')
        )
        materia.guardar()
        flash('Materia creada exitosamente.', 'success')
        return redirect(url_for('materias.listar_materias'))

    return render_template(
        'aplicacion/formularios/crear_materia.html',
        page_title='Crear Materia',
        active_page='materias'
    )


@materias_bp.route('/<int:materia_id>/editar', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
@accion_requerida('materias', 'editar')
def editar_materia(materia_id):
    materia = Materia.obtener_por_id(materia_id)
    if not materia:
        flash('Materia no encontrada.', 'error')
        return redirect(url_for('configuracion.configuracion') + '#materias')

    if request.method == 'POST':
        materia.nombre = request.form.get('nombre')
        materia.descripcion = request.form.get('descripcion')
        materia.actualizar()
        flash('Materia actualizada.', 'success')
        return redirect(url_for('configuracion.configuracion') + '#materias')

    return render_template(
        'aplicacion/formularios/crear_materia.html',
        page_title='Editar Materia',
        active_page='materias',
        materia=materia
    )


@materias_bp.route('/<int:materia_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('coordinador')
@accion_requerida('materias', 'eliminar')
def eliminar_materia(materia_id):
    materia = Materia.obtener_por_id(materia_id)
    if not materia:
        flash('Materia no encontrada.', 'error')
        return redirect(url_for('configuracion.configuracion') + '#materias')

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('materia', materia_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de materia',
            entidad_nombre=materia.nombre,
            entidad_id=materia_id,
            dependencias=dependencias,
            volver_url=request.referrer or (url_for('configuracion.configuracion') + '#materias')
        )

    try:
        materia.eliminar()
        flash('Materia eliminada.', 'success')
    except Exception:
        pass
    return redirect(url_for('configuracion.configuracion') + '#materias' )
