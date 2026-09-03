"""
Rutas del blueprint de Archivo Historico.
Repositorio de proyectos ya concluidos de cursos/cohortes anteriores,
con busqueda por texto, materia y cohorte.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import archivo_bp
from app.models import ProyectoArchivado, Materia, Cohorte
from app.decorators import login_required, roles_permitidos, modulo_requerido, eliminacion_segura


@archivo_bp.route('/')
@modulo_requerido('archivo')
def listar_archivo():
    """Busca y lista proyectos archivados, con filtros combinables y paginación."""
    texto = request.args.get('q', '').strip()
    materia_id = request.args.get('materia_id') or None
    cohorte_id = request.args.get('cohorte_id') or None

    # obtener lista completa (la función puede devolver list o iterable)
    if texto or materia_id or cohorte_id:
        proyectos_iter = ProyectoArchivado.buscar(texto=texto or None, materia_id=materia_id, cohorte_id=cohorte_id)
    else:
        proyectos_iter = ProyectoArchivado.obtener_todos()

    # normalizar a lista y aplicar paginación simple
    try:
        proyectos_list = list(proyectos_iter)
    except Exception:
        proyectos_list = [p for p in proyectos_iter]

    import math
    pagina = int(request.args.get('pagina', 1))
    por_pagina = 10
    total_proyectos = len(proyectos_list)
    total_paginas = max(1, math.ceil(total_proyectos / por_pagina))
    if pagina < 1:
        pagina = 1
    if pagina > total_paginas:
        pagina = total_paginas

    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    proyectos_page = proyectos_list[inicio:fin]

    return render_template(
        'aplicacion/archivo/archivo.html',
        page_title='Archivo Histórico',
        active_page='archivo',
        proyectos=proyectos_page,
        materias=Materia.obtener_todas(),
        cohortes=Cohorte.obtener_todos(),
        filtro_texto=texto,
        filtro_materia=int(materia_id) if materia_id else None,
        filtro_cohorte=int(cohorte_id) if cohorte_id else None,
        pagina=pagina,
        total_paginas=total_paginas,
        total_proyectos=total_proyectos
    )


@archivo_bp.route('/subir', methods=['GET', 'POST'])
@roles_permitidos('profesor', 'coordinador')
def subir_proyecto():
    """Archiva un proyecto concluido. Solo profesor/coordinador."""
    if request.method == 'POST':
        proyecto = ProyectoArchivado(
            titulo=request.form.get('titulo'),
            descripcion=request.form.get('descripcion'),
            autor=request.form.get('autor'),
            materia_id=request.form.get('materia_id') or None,
            cohorte_id=request.form.get('cohorte_id') or None,
            url_archivo=request.form.get('url_archivo'),
            palabras_clave=request.form.get('palabras_clave'),
            creado_por=session.get('usuario_id')
        )
        proyecto.guardar()
        flash('Proyecto archivado exitosamente.', 'success')
        return redirect(url_for('archivo.listar_archivo'))

    return render_template(
        'aplicacion/archivo/subir_proyecto.html',
        page_title='Archivar Proyecto',
        active_page='archivo',
        materias=Materia.obtener_todas(),
        cohortes=Cohorte.obtener_todos()
    )


@archivo_bp.route('/<int:proyecto_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('coordinador')
@eliminacion_segura
def eliminar_proyecto(proyecto_id):
    """Elimina un proyecto del archivo. Solo coordinador."""
    proyecto = ProyectoArchivado.obtener_por_id(proyecto_id)
    if not proyecto:
        flash('Proyecto no encontrado.', 'error')
        return redirect(url_for('archivo.listar_archivo'))

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('proyecto_archivado', proyecto_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de proyecto archivado',
            entidad_nombre=proyecto.titulo,
            entidad_id=proyecto_id,
            dependencias=dependencias,
            volver_url=request.referrer or url_for('archivo.listar_archivo')
        )

    proyecto.eliminar()
    flash('Proyecto eliminado del archivo.', 'success')
    return redirect(url_for('archivo.listar_archivo'))