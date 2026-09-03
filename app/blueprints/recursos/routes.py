"""
Rutas del blueprint de Recursos.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import recursos_bp
from app.models import Recurso, Materia, Curso
from app.decorators import login_required, roles_permitidos, modulo_requerido, eliminacion_segura


@recursos_bp.route('/')
@modulo_requerido('recursos')
def listar_recursos():
    """Lista recursos, opcionalmente filtrados por curso (para no mezclar
    material de un curso con el de otro)."""
    curso_id = request.args.get('curso_id', type=int)
    recursos_iter = Recurso.obtener_todos(curso_id=curso_id)

    # normalizar y paginar
    try:
        recursos_list = list(recursos_iter)
    except Exception:
        recursos_list = [r for r in recursos_iter]

    import math
    pagina = int(request.args.get('pagina', 1))
    por_pagina = 10
    total_recursos = len(recursos_list)
    total_paginas = max(1, math.ceil(total_recursos / por_pagina))
    if pagina < 1:
        pagina = 1
    if pagina > total_paginas:
        pagina = total_paginas
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    recursos_page = recursos_list[inicio:fin]

    return render_template(
        'aplicacion/recursos/recursos.html',
        page_title='Recursos',
        active_page='recursos',
        recursos=recursos_page,
        cursos=Curso.obtener_todos(),
        filtro_curso=curso_id,
        pagina=pagina,
        total_paginas=total_paginas,
        total_recursos=total_recursos
    )


@recursos_bp.route('/crear', methods=['GET', 'POST'])
@roles_permitidos('profesor', 'coordinador')
def form_crear_recurso():
    if request.method == 'POST':
        recurso = Recurso(
            titulo=request.form.get('titulo'),
            descripcion=request.form.get('descripcion'),
            url_archivo=request.form.get('url_archivo'),
            tipo=request.form.get('tipo'),
            materia_id=request.form.get('materia_id') or None,
            curso_id=request.form.get('curso_id') or None,
            creado_por=session.get('usuario_id')
        )
        recurso.guardar()
        flash('Recurso subido exitosamente.', 'success')
        return redirect(url_for('recursos.listar_recursos'))

    return render_template(
        'aplicacion/formularios/crear_recurso.html',
        page_title='Subir Recurso',
        active_page='recursos',
        materias=Materia.obtener_todas(),
        cursos=Curso.obtener_todos()
    )


@recursos_bp.route('/<int:recurso_id>/editar', methods=['GET', 'POST'])
@roles_permitidos('profesor', 'coordinador')
def editar_recurso(recurso_id):
    recurso = Recurso.obtener_por_id(recurso_id)
    if not recurso:
        flash('Recurso no encontrado.', 'error')
        return redirect(url_for('recursos.listar_recursos'))

    if session.get('rol') == 'profesor' and recurso.creado_por != session.get('usuario_id'):
        flash('Solo podés editar los recursos que vos mismo subiste.', 'error')
        return redirect(url_for('recursos.listar_recursos'))

    if request.method == 'POST':
        recurso.titulo = request.form.get('titulo')
        recurso.descripcion = request.form.get('descripcion')
        recurso.url_archivo = request.form.get('url_archivo')
        recurso.tipo = request.form.get('tipo')
        recurso.materia_id = request.form.get('materia_id') or None
        recurso.curso_id = request.form.get('curso_id') or None
        recurso.actualizar()
        flash('Recurso actualizado.', 'success')
        return redirect(url_for('recursos.listar_recursos'))

    return render_template(
        'aplicacion/formularios/crear_recurso.html',
        page_title='Editar Recurso',
        active_page='recursos',
        recurso=recurso,
        materias=Materia.obtener_todas(),
        cursos=Curso.obtener_todos()
    )


@recursos_bp.route('/<int:recurso_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('profesor', 'coordinador')
@eliminacion_segura
def eliminar_recurso(recurso_id):
    recurso = Recurso.obtener_por_id(recurso_id)
    if not recurso:
        flash('Recurso no encontrado.', 'error')
        return redirect(url_for('recursos.listar_recursos'))

    if session.get('rol') == 'profesor' and recurso.creado_por != session.get('usuario_id'):
        flash('Solo podés eliminar los recursos que vos mismo subiste.', 'error')
        return redirect(url_for('recursos.listar_recursos'))

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('recurso', recurso_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de recurso',
            entidad_nombre=recurso.titulo,
            entidad_id=recurso_id,
            dependencias=dependencias,
            volver_url=request.referrer or url_for('recursos.listar_recursos')
        )

    recurso.eliminar()
    flash('Recurso eliminado.', 'success')
    return redirect(url_for('recursos.listar_recursos'))