"""
Rutas del blueprint de Grupos.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import grupos_bp
from app.models import Grupo, Materia
from app.decorators import login_required, roles_permitidos, modulo_requerido, accion_requerida, eliminacion_segura


@grupos_bp.route('/')
@modulo_requerido('grupos')
def listar_grupos():
    """Lista todos los grupos, paginados."""
    todos = Grupo.obtener_todos()
    por_pagina = 20
    pagina = request.args.get('pagina', 1, type=int)
    total_paginas = max(1, (len(todos) + por_pagina - 1) // por_pagina)
    pagina = min(max(pagina, 1), total_paginas)
    grupos = todos[(pagina - 1) * por_pagina: pagina * por_pagina]
    return render_template(
        'aplicacion/grupos/grupos.html',
        page_title='Grupos',
        active_page='grupos',
        grupos=grupos,
        pagina=pagina,
        total_paginas=total_paginas,
        total_grupos=len(todos)
    )


@grupos_bp.route('/crear', methods=['GET', 'POST'])
@roles_permitidos('profesor', 'coordinador')
@accion_requerida('grupos', 'crear')
def form_crear_grupo():
    if request.method == 'POST':
        grupo = Grupo(
            nombre=request.form.get('nombre'),
            descripcion=request.form.get('descripcion'),
            materia_id=request.form.get('materia_id') or None,
            creado_por=session.get('usuario_id')
        )
        try:
            grupo.guardar()
            flash('Grupo creado exitosamente.', 'success')
            return redirect(url_for('grupos.listar_grupos'))
        except ValueError as e:
            flash(str(e), 'error')

    materias = Materia.obtener_todas()
    return render_template(
        'aplicacion/formularios/crear_grupo.html',
        page_title='Crear Grupo',
        active_page='grupos',
        materias=materias
    )


@grupos_bp.route('/<int:grupo_id>/editar', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
@accion_requerida('grupos', 'editar')
def editar_grupo(grupo_id):
    grupo = Grupo.obtener_por_id(grupo_id)
    if not grupo:
        flash('Grupo no encontrado.', 'error')
        return redirect(url_for('configuracion.configuracion') + '#grupos')

    if request.method == 'POST':
        grupo.nombre = request.form.get('nombre')
        grupo.descripcion = request.form.get('descripcion')
        grupo.materia_id = request.form.get('materia_id') or None
        grupo.actualizar()
        flash('Grupo actualizado.', 'success')
        return redirect(url_for('configuracion.configuracion') + '#grupos')

    materias = Materia.obtener_todas()
    return render_template(
        'aplicacion/formularios/crear_grupo.html',
        page_title='Editar Grupo',
        active_page='grupos',
        grupo=grupo,
        materias=materias
    )


@grupos_bp.route('/<int:grupo_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('coordinador')
@accion_requerida('grupos', 'eliminar')
@eliminacion_segura
def eliminar_grupo(grupo_id):
    grupo = Grupo.obtener_por_id(grupo_id)
    if not grupo:
        flash('Grupo no encontrado.', 'error')
        return redirect(url_for('configuracion.configuracion') + '#grupos')

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('grupo', grupo_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de grupo',
            entidad_nombre=grupo.nombre,
            entidad_id=grupo_id,
            dependencias=dependencias,
            volver_url=request.referrer or (url_for('configuracion.configuracion') + '#grupos')
        )

    try:
        grupo.eliminar()
        flash('Grupo eliminado.', 'success')
    except Exception:
        pass
    return redirect(url_for('configuracion.configuracion') + '#grupos')