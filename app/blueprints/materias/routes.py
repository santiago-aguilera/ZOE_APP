"""
Rutas del blueprint de Materias.
Catálogo reutilizable de materias, independiente de cohorte y curso.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import materias_bp
from app.models import Materia, Descriptor, Cohorte
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

    cohorte_id = request.args.get('cohorte_id', type=int) or session.get('cohorte_activa_id')
    cohortes = Cohorte.obtener_todos()
    if not cohorte_id and cohortes:
        cohorte_id = cohortes[0].id

    return render_template(
        'aplicacion/materias/ver_materia.html',
        page_title=materia.nombre,
        active_page='materias',
        materia=materia,
        asignaciones=Materia.obtener_asignaciones(materia_id),
        cohortes=cohortes,
        cohorte_id=cohorte_id,
        descriptor=Descriptor.obtener_por_materia_cohorte(materia_id, cohorte_id) if cohorte_id else None
    )


@materias_bp.route('/crear', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
@accion_requerida('materias', 'crear')
def form_crear_materia():
    if request.method == 'POST':
        materia = Materia(
            nombre=request.form.get('nombre'),
            descripcion=request.form.get('descripcion'),
            tipo=request.form.get('tipo', 'normal')
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
        materia.tipo = request.form.get('tipo', materia.tipo)
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


# ---------------------------------------------------------------
# Descriptores: uno por materia individual (troncal o normal), por
# cohorte/año. Copiables de una cohorte anterior, editables.
# ---------------------------------------------------------------

@materias_bp.route('/<int:materia_id>/descriptores/guardar', methods=['POST'])
@roles_permitidos('coordinador', 'profesor')
@accion_requerida('descriptores', 'crear')
def guardar_descriptor(materia_id):
    """Crea o edita el descriptor de la materia para la cohorte indicada."""
    cohorte_id = request.form.get('cohorte_id', type=int)
    if not cohorte_id:
        flash('Seleccioná una cohorte para el descriptor.', 'error')
        return redirect(url_for('materias.ver_materia', materia_id=materia_id))

    existente = Descriptor.obtener_por_materia_cohorte(materia_id, cohorte_id)
    if existente:
        existente.texto = request.form.get('texto')
        existente.requisitos = request.form.get('requisitos')
        existente.evidencia_esperada = request.form.get('evidencia_esperada')
        existente.actualizar()
        flash('Descriptor actualizado.', 'success')
    else:
        nuevo = Descriptor(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            texto=request.form.get('texto'),
            requisitos=request.form.get('requisitos'),
            evidencia_esperada=request.form.get('evidencia_esperada'),
            creado_por=session.get('usuario_id')
        )
        nuevo.guardar()
        flash('Descriptor creado.', 'success')
    return redirect(url_for('materias.ver_materia', materia_id=materia_id, cohorte_id=cohorte_id))


@materias_bp.route('/descriptores/copiar', methods=['POST'])
@roles_permitidos('coordinador')
@accion_requerida('descriptores', 'crear')
def copiar_descriptores():
    """Copia todos los descriptores de una cohorte anterior a la cohorte
    nueva, para no redefinirlos desde cero (quedan editables después)."""
    cohorte_origen_id = request.form.get('cohorte_origen_id', type=int)
    cohorte_destino_id = request.form.get('cohorte_destino_id', type=int)
    if not cohorte_origen_id or not cohorte_destino_id:
        flash('Seleccioná la cohorte de origen y la de destino.', 'error')
        return redirect(request.referrer or url_for('materias.listar_materias'))

    copiados = Descriptor.copiar_de_cohorte(cohorte_origen_id, cohorte_destino_id, session.get('usuario_id'))
    flash(f'Se copiaron {copiados} descriptores a la nueva cohorte.', 'success')
    return redirect(request.referrer or url_for('materias.listar_materias'))
