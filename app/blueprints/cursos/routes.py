"""
Rutas del blueprint de Cursos.

Un curso (1001-1004 décimo, 1101-1104 once) es un catálogo GLOBAL e
INDEPENDIENTE de las cohortes: se reutiliza cohorte tras cohorte. La
cohorte es solo un filtro de contexto (qué estudiantes de esa cohorte
están hoy en este curso), nunca una dependencia estructural.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import cursos_bp
from app.models import Curso, Cohorte, Materia, Usuario, GRADOS_CURSO
from app.decorators import login_required, roles_permitidos, modulo_requerido, accion_requerida


@cursos_bp.route('/')
@modulo_requerido('cursos')
def listar_cursos():
    """Lista todos los cursos del catálogo. La cohorte es solo un filtro
    para el conteo de estudiantes, no una propiedad del curso."""
    cohorte_id = request.args.get('cohorte_id', type=int)
    cursos_iter = Curso.obtener_todos(cohorte_id=cohorte_id)
    cohortes = Cohorte.obtener_todos()

    # normalizar a lista y paginar
    try:
        cursos_list = list(cursos_iter)
    except Exception:
        cursos_list = [c for c in cursos_iter]

    import math
    pagina = int(request.args.get('pagina', 1))
    por_pagina = 10
    total_cursos = len(cursos_list)
    total_paginas = max(1, math.ceil(total_cursos / por_pagina))
    if pagina < 1:
        pagina = 1
    if pagina > total_paginas:
        pagina = total_paginas
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    cursos_page = cursos_list[inicio:fin]

    return render_template(
        'aplicacion/cursos/cursos.html',
        page_title='Cursos',
        active_page='cursos',
        cursos=cursos_page,
        cohortes=cohortes,
        filtro_cohorte=cohorte_id,
        pagina=pagina,
        total_paginas=total_paginas,
        total_cursos=total_cursos
    )


@cursos_bp.route('/crear', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
@accion_requerida('cursos', 'crear')
def form_crear_curso():
    """Alta manual de un curso (los 8 oficiales ya vienen precargados;
    esto permite agregar secciones nuevas si la institución las necesita)."""
    if request.method == 'POST':
        curso = Curso(
            codigo=request.form.get('codigo'),
            nombre=request.form.get('nombre') or request.form.get('codigo'),
            grado=request.form.get('grado', type=int),
            seccion=request.form.get('seccion', type=int)
        )
        curso.guardar()
        flash('Curso creado exitosamente.', 'success')
        return redirect(url_for('cursos.listar_cursos'))

    return render_template(
        'aplicacion/formularios/crear_curso.html',
        page_title='Crear Curso',
        active_page='cursos',
        grados=GRADOS_CURSO
    )


@cursos_bp.route('/<int:curso_id>/editar', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
@accion_requerida('cursos', 'editar')
def editar_curso(curso_id):
    curso = Curso.obtener_por_id(curso_id)
    if not curso:
        flash('Curso no encontrado.', 'error')
        return redirect(url_for('cursos.listar_cursos'))

    if request.method == 'POST':
        curso.codigo = request.form.get('codigo')
        curso.nombre = request.form.get('nombre') or curso.codigo
        curso.grado = request.form.get('grado', type=int)
        curso.seccion = request.form.get('seccion', type=int)
        curso.activo = request.form.get('activo') == '1'
        curso.actualizar()
        flash('Curso actualizado.', 'success')
        return redirect(url_for('cursos.ver_curso', curso_id=curso.id))

    return render_template(
        'aplicacion/formularios/crear_curso.html',
        page_title='Editar Curso',
        active_page='cursos',
        curso=curso,
        grados=GRADOS_CURSO
    )


@cursos_bp.route('/<int:curso_id>/activar', methods=['POST'])
@roles_permitidos('coordinador')
def toggle_activo(curso_id):
    """Activa o desactiva un curso (más seguro que eliminarlo si tiene historial)."""
    curso = Curso.obtener_por_id(curso_id)
    if curso:
        curso.activo = not curso.activo
        curso.actualizar()
        flash(f'Curso {"activado" if curso.activo else "desactivado"}.', 'success')
    return redirect(request.referrer or url_for('cursos.listar_cursos'))


@cursos_bp.route('/<int:curso_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('coordinador')
@accion_requerida('cursos', 'eliminar')
def eliminar_curso(curso_id):
    """Elimina un curso. Muestra dependencias antes de borrar."""
    curso = Curso.obtener_por_id(curso_id)
    if not curso:
        flash('Curso no encontrado.', 'error')
        return redirect(url_for('cursos.listar_cursos'))

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('curso', curso_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de curso',
            entidad_nombre=curso.nombre or curso.codigo,
            entidad_id=curso_id,
            dependencias=dependencias,
            volver_url=request.referrer or url_for('cursos.listar_cursos')
        )

    try:
        curso.eliminar()
        flash('Curso eliminado.', 'success')
    except Exception:
        flash('No se puede eliminar: el curso todavía tiene estudiantes o materias asignadas. Desactivalo en su lugar.', 'error')
    return redirect(url_for('cursos.listar_cursos'))


@cursos_bp.route('/<int:curso_id>')
@login_required
def ver_curso(curso_id):
    """Detalle de un curso, organizado por secciones: información general,
    materias, profesores, estudiantes y grupos de estudio."""
    curso = Curso.obtener_por_id(curso_id)
    if not curso:
        flash('Curso no encontrado.', 'error')
        return redirect(url_for('cursos.listar_cursos'))

    cohorte_id = request.args.get('cohorte_id', type=int)
    cohortes = Cohorte.obtener_todos()
    estudiantes = Curso.obtener_estudiantes(curso_id, cohorte_id=cohorte_id)
    materias_curso = Curso.obtener_materias(curso_id)
    profesores_curso = Curso.obtener_profesores(curso_id)
    grupos_curso = Curso.obtener_grupos(curso_id)

    todos_usuarios = Usuario.obtener_todos()
    estudiantes_ids_actuales = {e['usuario_id'] for e in estudiantes}
    materias_ids_actuales = {m['materia_id'] for m in materias_curso}

    estudiantes_disponibles = [
        u for u in todos_usuarios
        if u.rol == 'estudiante' and u.id not in estudiantes_ids_actuales
    ]
    profesores = [u for u in todos_usuarios if u.rol == 'profesor']
    materias_disponibles = [
        m for m in Materia.obtener_todas() if m.id not in materias_ids_actuales
    ]

    return render_template(
        'aplicacion/cursos/ver_curso.html',
        page_title=f'Curso {curso.codigo}',
        active_page='cursos',
        curso=curso,
        cohortes=cohortes,
        filtro_cohorte=cohorte_id,
        estudiantes=estudiantes,
        materias_curso=materias_curso,
        profesores_curso=profesores_curso,
        grupos_curso=grupos_curso,
        estudiantes_disponibles=estudiantes_disponibles,
        profesores=profesores,
        materias_disponibles=materias_disponibles
    )


@cursos_bp.route('/<int:curso_id>/estudiantes/agregar', methods=['POST'])
@roles_permitidos('coordinador')
@accion_requerida('cursos', 'asignar')
def agregar_estudiante(curso_id):
    """Asigna un estudiante a este curso."""
    estudiante_id = request.form.get('estudiante_id')
    if estudiante_id:
        Curso.inscribir_estudiante(curso_id, estudiante_id)
        flash('Estudiante asignado al curso.', 'success')
    return redirect(url_for('cursos.ver_curso', curso_id=curso_id))


@cursos_bp.route('/<int:curso_id>/estudiantes/<int:estudiante_id>/quitar', methods=['POST'])
@roles_permitidos('coordinador')
def quitar_estudiante(curso_id, estudiante_id):
    """Quita a un estudiante de este curso."""
    Curso.quitar_estudiante(estudiante_id)
    flash('Estudiante removido del curso.', 'success')
    return redirect(url_for('cursos.ver_curso', curso_id=curso_id))


@cursos_bp.route('/<int:curso_id>/materias/agregar', methods=['POST'])
@roles_permitidos('coordinador')
@accion_requerida('cursos', 'asignar')
def agregar_materia(curso_id):
    """Agrega una materia al paquete del curso (asignación académica), con
    su profesor (opcional): MATERIA -> ASIGNACIÓN ACADÉMICA -> CURSO + PROFESOR."""
    materia_id = request.form.get('materia_id')
    profesor_id = request.form.get('profesor_id') or None
    if materia_id:
        Curso.asignar_materia(curso_id, materia_id, profesor_id)
        flash('Materia agregada al curso.', 'success')
    return redirect(url_for('cursos.ver_curso', curso_id=curso_id))


@cursos_bp.route('/<int:curso_id>/materias/<int:curso_materia_id>/quitar', methods=['POST'])
@roles_permitidos('coordinador')
def quitar_materia(curso_id, curso_materia_id):
    """Quita una materia del paquete del curso."""
    Curso.quitar_materia(curso_materia_id)
    flash('Materia removida del curso.', 'success')
    return redirect(url_for('cursos.ver_curso', curso_id=curso_id))


@cursos_bp.route('/<int:curso_id>/materias/<int:curso_materia_id>/profesor', methods=['POST'])
@roles_permitidos('coordinador')
@accion_requerida('cursos', 'asignar')
def asignar_profesor(curso_id, curso_materia_id):
    """Asigna o cambia el profesor que dicta una materia dentro del curso
    (un profesor puede dictar la misma materia en varios cursos, y distintos
    cursos de la misma materia pueden tener distinto profesor)."""
    profesor_id = request.form.get('profesor_id') or None
    Curso.asignar_profesor_materia(curso_materia_id, profesor_id)
    flash('Profesor asignado.', 'success')
    return redirect(url_for('cursos.ver_curso', curso_id=curso_id))
