"""
Rutas del blueprint de Usuarios.

Un estudiante tiene, de forma directa: usuario, cohorte, curso y estado de
matrícula BI (NO_MATRICULADO por defecto — ver nota técnica en models.py).
"""

from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from app.blueprints import usuarios_bp
from app.models import Usuario, Cohorte, Curso, ESTADOS_MATRICULA, ETIQUETAS_ESTADO_MATRICULA, RolPermiso
from app.decorators import roles_permitidos, eliminacion_segura, accion_requerida


@usuarios_bp.route('/')
@roles_permitidos('coordinador')
def listar_usuarios():
    """Lista usuarios, con filtros combinables: cohorte + curso + estado de
    matrícula BI + rol. Se resuelven realmente en la consulta SQL."""
    cohorte_id = request.args.get('cohorte_id', type=int)
    curso_id = request.args.get('curso_id', type=int)
    estado_matricula = request.args.get('estado_matricula') or None
    rol = request.args.get('rol') or None

    usuarios_iter = Usuario.obtener_todos(cohorte_id=cohorte_id, curso_id=curso_id,
                                      estado_matricula=estado_matricula, rol=rol)

    # normalizar y paginar
    try:
        usuarios_list = list(usuarios_iter)
    except Exception:
        usuarios_list = [u for u in usuarios_iter]

    import math
    pagina = int(request.args.get('pagina', 1))
    por_pagina = 10
    total_usuarios = len(usuarios_list)
    total_paginas = max(1, math.ceil(total_usuarios / por_pagina))
    if pagina < 1:
        pagina = 1
    if pagina > total_paginas:
        pagina = total_paginas
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    usuarios_page = usuarios_list[inicio:fin]

    return render_template(
        'aplicacion/usuarios/usuarios.html',
        page_title='Usuarios',
        active_page='usuarios',
        usuarios=usuarios_page,
        cohortes=Cohorte.obtener_todos(),
        cursos=Curso.obtener_todos(),
        estados_matricula=ESTADOS_MATRICULA,
        etiquetas_estado=ETIQUETAS_ESTADO_MATRICULA,
        filtro_cohorte=cohorte_id,
        filtro_curso=curso_id,
        filtro_estado=estado_matricula,
        filtro_rol=rol,
        pagina=pagina,
        total_paginas=total_paginas,
            total_usuarios=total_usuarios,
            rol=session.get('rol', 'invitado')
        )


@usuarios_bp.route('/crear', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
@accion_requerida('usuarios', 'crear')
def form_crear_usuario():
    if request.method == 'POST':
        rol_nuevo = request.form.get('rol')
        usuario = Usuario(
            id=request.form.get('id'),
            nombre=request.form.get('nombre'),
            correo=request.form.get('correo'),
            contrasena_hash=generate_password_hash(request.form.get('contrasena')),
            rol=rol_nuevo,
            cohorte_id=request.form.get('cohorte_id') or None,
            curso_id=(request.form.get('curso_id') or None) if rol_nuevo == 'estudiante' else None
            # estado_matricula no se pasa: todo estudiante nuevo arranca en
            # NO_MATRICULADO por defecto (ver models.py).
        )
        usuario.guardar()
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('usuarios.listar_usuarios'))

    return render_template(
        'aplicacion/formularios/crear_usuario.html',
        page_title='Crear Usuario',
        active_page='usuarios',
        cohortes=Cohorte.obtener_todos(),
        cursos=Curso.obtener_todos(),
        estados_matricula=ESTADOS_MATRICULA,
        etiquetas_estado=ETIQUETAS_ESTADO_MATRICULA,
        usuarios=None
    )

        
    


    



@usuarios_bp.route('/<int:usuario_id>/editar', methods=['GET', 'POST'])
@roles_permitidos('coordinador')
@accion_requerida('usuarios', 'editar')
def editar_usuario(usuario_id):
    usuario = Usuario.obtener_por_id(usuario_id)
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('usuarios.listar_usuarios'))

    if request.method == 'POST':
        usuario.nombre = request.form.get('nombre')
        usuario.correo = request.form.get('correo')
        usuario.rol = request.form.get('rol')
        usuario.cohorte_id = request.form.get('cohorte_id') or None
        usuario.curso_id = request.form.get('curso_id') if usuario.rol == 'estudiante' else None
        usuario.activo = request.form.get('activo') == 'on'
        usuario.actualizar()

        if usuario.rol == 'estudiante':
            nuevo_estado = request.form.get('estado_matricula')
            if nuevo_estado in ESTADOS_MATRICULA and nuevo_estado != usuario.estado_matricula:
                if not RolPermiso.tiene_permiso_accion(session.get('rol'), 'matricula', 'cambiar_estado'):
                    flash('No tenés permiso para cambiar el estado de matrícula.', 'error')
                    return redirect(url_for('configuracion.configuracion') + '#usuarios')
                usuario.cambiar_estado_matricula(nuevo_estado, registrado_por=session.get('usuario_id'))

        nueva_contrasena = request.form.get('contrasena')
        if nueva_contrasena:
            usuario.cambiar_contrasena(generate_password_hash(nueva_contrasena))

        flash('Usuario actualizado.', 'success')
        return redirect(url_for('configuracion.configuracion') + '#usuarios')

    return render_template(
        'aplicacion/formularios/crear_usuario.html',
        page_title='Editar Usuario',
        active_page='usuarios',
        usuario_obj=usuario,
        cohortes=Cohorte.obtener_todos(),
        cursos=Curso.obtener_todos(),
        estados_matricula=ESTADOS_MATRICULA,
        etiquetas_estado=ETIQUETAS_ESTADO_MATRICULA
    )


@usuarios_bp.route('/<int:usuario_id>/eliminar', methods=['GET','POST'])
@roles_permitidos('coordinador')
@accion_requerida('usuarios', 'eliminar')
@eliminacion_segura
def eliminar_usuario(usuario_id):
    if usuario_id == session.get('usuario_id'):
        flash('No podés eliminar tu propio usuario.', 'error')
        return redirect(url_for('configuracion.configuracion') + '#usuarios')

    usuario = Usuario.obtener_por_id(usuario_id)
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('configuracion.configuracion') + '#usuarios')

    from app.delete_helpers import listar_dependencias
    # Mostrar confirmación con dependencias antes de borrar
    if request.method == 'GET':
        dependencias = listar_dependencias('usuario', usuario_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de usuario',
            entidad_nombre=usuario.nombre,
            entidad_id=usuario_id,
            dependencias=dependencias,
            volver_url=request.referrer or (url_for('configuracion.configuracion') + '#usuarios')
        )

    # POST: eliminar. La BD aplica CASCADE/SET NULL/RESTRICT segun corresponda;
    try:
        eliminado = usuario.eliminar()
        if eliminado:
            flash('Usuario eliminado.', 'success')
        else:
            flash('No se pudo eliminar el usuario.', 'error')
    except Exception:
        # el decorador eliminacion_segura mostrará un mensaje amigable
        pass
    return redirect(url_for('configuracion.configuracion') + '#usuarios')
