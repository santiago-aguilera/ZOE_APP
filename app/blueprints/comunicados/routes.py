"""
Rutas del blueprint de Comunicados.
Anuncios visibles para TODOS los grupos y profesores (broadcast global,
no se filtra por materia/grupo — es información institucional general).
"""

from flask import render_template, request, redirect, url_for, session, flash
from app.blueprints import comunicados_bp
from app.models import Comunicado
from app.decorators import login_required, roles_permitidos, modulo_requerido, eliminacion_segura


@comunicados_bp.route('/')
@modulo_requerido('comunicados')
def listar_comunicados():
    """Lista todos los comunicados activos."""
    comunicados = Comunicado.obtener_activos()
    return render_template(
        'aplicacion/informacion/informacion.html',
        page_title='Información',
        active_page='informacion',
        comunicados=comunicados
    )


@comunicados_bp.route('/crear', methods=['GET', 'POST'])
@roles_permitidos('profesor', 'coordinador')
def crear_comunicado():
    """Publica un nuevo comunicado, visible para todos."""
    if request.method == 'POST':
        comunicado = Comunicado(
            titulo=request.form.get('titulo'),
            contenido=request.form.get('contenido'),
            creado_por=session.get('usuario_id')
        )
        comunicado.guardar()
        flash('Comunicado publicado.', 'success')
        return redirect(url_for('comunicados.listar_comunicados'))

    return render_template(
        'aplicacion/formularios/crear_comunicado.html',
        page_title='Publicar Comunicado',
        active_page='informacion'
    )


@comunicados_bp.route('/<int:comunicado_id>/editar', methods=['GET', 'POST'])
@roles_permitidos('profesor', 'coordinador')
def editar_comunicado(comunicado_id):
    comunicado = Comunicado.obtener_por_id(comunicado_id)
    if not comunicado:
        flash('Comunicado no encontrado.', 'error')
        return redirect(url_for('comunicados.listar_comunicados'))

    if session.get('rol') != 'coordinador' and comunicado.creado_por != session.get('usuario_id'):
        flash('Solo podés editar los comunicados que vos mismo publicaste.', 'error')
        return redirect(url_for('comunicados.listar_comunicados'))

    if request.method == 'POST':
        comunicado.titulo = request.form.get('titulo')
        comunicado.contenido = request.form.get('contenido')
        comunicado.actualizar()
        flash('Comunicado actualizado.', 'success')
        return redirect(url_for('comunicados.listar_comunicados'))

    return render_template(
        'aplicacion/formularios/crear_comunicado.html',
        page_title='Editar Comunicado',
        active_page='informacion',
        comunicado=comunicado
    )


@comunicados_bp.route('/<int:comunicado_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('profesor', 'coordinador')
@eliminacion_segura
def eliminar_comunicado(comunicado_id):
    comunicado = Comunicado.obtener_por_id(comunicado_id)
    if not comunicado:
        flash('Comunicado no encontrado.', 'error')
        return redirect(url_for('comunicados.listar_comunicados'))

    if session.get('rol') != 'coordinador' and comunicado.creado_por != session.get('usuario_id'):
        flash('Solo podés eliminar los comunicados que vos mismo publicaste.', 'error')
        return redirect(url_for('comunicados.listar_comunicados'))

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('comunicado', comunicado_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de comunicado',
            entidad_nombre=comunicado.titulo,
            entidad_id=comunicado_id,
            dependencias=dependencias,
            volver_url=request.referrer or url_for('comunicados.listar_comunicados')
        )

    comunicado.eliminar()
    flash('Comunicado eliminado.', 'success')
    return redirect(url_for('comunicados.listar_comunicados'))
