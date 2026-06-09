"""
Aplicación web ZOE — punto de entrada.

Autenticación, rutas protegidas y CRUDs completos contra MySQL.
Modelos SQLAlchemy en app/model/.
"""

import sys
from pathlib import Path
from datetime import datetime, date
from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for, flash

from config import Config

# -----------------------------------------------------------------------------
# Rutas del proyecto
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# -----------------------------------------------------------------------------
# Importación de SQLAlchemy db y todos los modelos
# -----------------------------------------------------------------------------
from app.model import (
    db,
    Usuario, Estudiante, Profesor, Coordinador,
    Materia, ProfesorMateria, EstudianteMateria,
    Grupo, EstudianteGrupo,
    Tarea, Entrega,
    Comunicado, Mensaje, Cronograma, Recurso,
    PeriodoAcademico,
)

# -----------------------------------------------------------------------------
# Inicialización de Flask
# -----------------------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=str(Config.TEMPLATES_FOLDER),
    static_folder=str(Config.STATIC_FOLDER),
    static_url_path="/static",
)

app.config.from_object(Config)
db.init_app(app)


# =============================================================================
# DECORADORES DE AUTENTICACIÓN Y AUTORIZACIÓN
# =============================================================================
def login_requerido(f):
    """Protege rutas: redirige al login si no hay sesión activa."""
    @wraps(f)
    def decorada(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorada


def rol_requerido(*roles_permitidos):
    """Restringe el acceso según el rol del usuario en sesión."""
    def decorador(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            rol = session.get("rol", "")
            if rol not in roles_permitidos:
                flash(f"Acceso restringido. Se requiere rol: {', '.join(roles_permitidos)}", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorada
    return decorador


# =============================================================================
# CONTEXT PROCESSOR — variables globales para Jinja2
# =============================================================================
@app.context_processor
def variables_globales():
    usuario_actual = None
    if "user_id" in session:
        usuario_actual = Usuario.query.get(session["user_id"])
    return {
        "app_name": "ZOE IB",
        "usuario_actual": usuario_actual,
        "rol": session.get("rol", ""),
    }


# =============================================================================
# HELPERS
# =============================================================================
def _pagina(template, titulo, pagina_activa):
    return render_template(template, page_title=titulo, active_page=pagina_activa)


def _aplicacion(template, titulo, pagina_activa, **kwargs):
    usuario = session.get("usuario", "Usuario")
    rol = session.get("rol", "estudiante")
    defaults = {"rol": rol, "usuario": usuario}
    defaults.update(kwargs)
    return render_template(
        template, page_title=titulo, active_page=pagina_activa, **defaults
    )


# =============================================================================
# AUTENTICACIÓN — Login / Logout
# =============================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login real: valida contra la tabla USUARIO.
    Usa el método POO Usuario.autenticar(correo, contrasena_hash).
    """
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        correo = request.form.get("email", "").strip()
        contrasena = request.form.get("password", "").strip()

        if not correo or not contrasena:
            flash("Correo y contraseña son obligatorios.", "danger")
            return _aplicacion("aplicacion/auth/login.html", "Login", "login")

        # Método POO: autenticar contra la BD
        usuario = Usuario.autenticar(correo, contrasena)
        if usuario:
            session["user_id"] = usuario.id
            session["usuario"] = usuario.nombre
            session["rol"] = usuario.rol
            flash(f"Bienvenido/a {usuario.nombre}", "success")
            return redirect(url_for("dashboard"))

        flash("Credenciales incorrectas.", "danger")
        return _aplicacion("aplicacion/auth/login.html", "Login", "login")

    return _aplicacion("aplicacion/auth/login.html", "Login", "login")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))


# =============================================================================
# INICIO Y DASHBOARD
# =============================================================================
@app.route("/")
def inicio():
    return _pagina("pagina/index.html", "Inicio", "index")


@app.route("/dashboard")
@login_requerido
def dashboard():
    """Dashboard protegido: muestra datos reales según el rol."""
    rol = session.get("rol", "estudiante")
    usuario_id = session.get("user_id")

    # Estadísticas según el rol (100% desde la BD)
    stats = {
        "total_materias": Materia.query.count(),
        "total_tareas": Tarea.query.count(),
        "total_usuarios": Usuario.query.count(),
        "total_entregas": Entrega.query.count(),
        "total_mensajes": Mensaje.query.count(),
        "comunicados_activos": Comunicado.query.filter_by(activo=True).count(),
        "total_estudiantes": Usuario.query.filter_by(rol="Estudiante").count(),
        "total_profesores": Usuario.query.filter_by(rol="Profesor").count(),
        "mensajes_no_leidos": Mensaje.query.filter_by(
            destinatario_id=usuario_id, leido=False
        ).count(),
    }

    if rol == "Estudiante":
        # Materias del estudiante (a través de ESTUDIANTE_MATERIA)
        from app.model import EstudianteMateria
        mis_materias_ids = [
            em.materia_id for em in EstudianteMateria.query.filter_by(usuario_id=usuario_id).all()
        ]
        stats["mis_materias"] = len(mis_materias_ids)
        stats["tareas_pendientes"] = Entrega.query.filter_by(
            estudiante_id=usuario_id, estado="Pendiente"
        ).count()
        stats["entregas_realizadas"] = Entrega.query.filter_by(
            estudiante_id=usuario_id
        ).filter(Entrega.estado != "Pendiente").count()
        # Próximas tareas
        from datetime import date
        proximas_tareas = Tarea.query.filter(
            Tarea.materia_id.in_(mis_materias_ids) if mis_materias_ids else False,
            Tarea.fecha_limite >= date.today(),
        ).order_by(Tarea.fecha_limite.asc()).limit(4).all() if mis_materias_ids else []
    elif rol == "Profesor":
        from app.model import ProfesorMateria
        mis_materias_ids = [
            pm.materia_id for pm in ProfesorMateria.query.filter_by(usuario_id=usuario_id).all()
        ]
        stats["mis_materias"] = len(mis_materias_ids)
        stats["mis_tareas"] = Tarea.query.filter(
            Tarea.materia_id.in_(mis_materias_ids) if mis_materias_ids else False
        ).count() if mis_materias_ids else 0
        stats["entregas_pendientes"] = Entrega.query.filter_by(estado="Pendiente").count()
        proximas_tareas = []
    else:
        # Coordinador
        proximas_tareas = []

    comunicados = Comunicado.query.filter_by(activo=True)\
        .order_by(Comunicado.publicado_en.desc()).limit(3).all()

    return _aplicacion(
        "aplicacion/dashboard.html", "Dashboard", "dashboard",
        stats=stats, comunicados=comunicados, proximas_tareas=proximas_tareas,
    )


# =============================================================================
# USUARIOS — CRUD completo
# =============================================================================
@app.route("/usuarios")
@login_requerido
def usuarios():
    """Lista todos los usuarios reales desde la BD."""
    usuarios = Usuario.query.all()
    return _aplicacion("aplicacion/usuarios/usuarios.html", "Usuarios", "usuarios", usuarios=usuarios)


@app.route("/usuarios/crear", methods=["GET", "POST"])
@rol_requerido("Coordinador")
def usuarios_crear():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        contrasena = request.form.get("contrasena", "").strip()
        rol = request.form.get("rol", "Estudiante").strip()
        periodo_id = request.form.get("periodo_id") or None

        errores = []
        if not nombre: errores.append("El nombre es obligatorio.")
        if not correo: errores.append("El correo es obligatorio.")
        if not contrasena: errores.append("La contraseña es obligatoria.")

        if not errores:
            try:
                if rol == "Profesor":
                    nuevo = Profesor(nombre=nombre, correo=correo, contrasena_hash=contrasena)
                elif rol == "Coordinador":
                    nuevo = Coordinador(nombre=nombre, correo=correo, contrasena_hash=contrasena)
                else:
                    nuevo = Estudiante(nombre=nombre, correo=correo, contrasena_hash=contrasena)

                if periodo_id:
                    nuevo.periodo_id = int(periodo_id)

                # SQL: INSERT INTO USUARIO ...
                db.session.add(nuevo)
                db.session.commit()
                flash(f"Usuario {nombre} creado correctamente.", "success")
                return redirect(url_for("usuarios"))
            except Exception as e:
                db.session.rollback()
                errores.append(f"Error al crear usuario: {e}")

        periodos = PeriodoAcademico.query.all()
        return _aplicacion(
            "aplicacion/formularios/crear_usuario.html", "Crear Usuario", "usuarios",
            errores=errores, periodos=periodos,
        )

    periodos = PeriodoAcademico.query.all()
    return _aplicacion(
        "aplicacion/formularios/crear_usuario.html", "Crear Usuario", "usuarios",
        periodos=periodos,
    )


@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
@rol_requerido("Coordinador")
def usuarios_editar(id):
    """Editar un usuario (UPDATE)."""
    usuario = Usuario.query.get_or_404(id)
    if request.method == "POST":
        try:
            usuario.set_nombre(request.form.get("nombre", usuario.nombre))
            usuario.set_correo(request.form.get("correo", usuario.correo))
            # SQL: UPDATE USUARIO SET ... WHERE id=?
            db.session.commit()
            flash("Usuario actualizado.", "success")
            return redirect(url_for("usuarios"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")
    return _aplicacion("aplicacion/usuarios/usuarios_edit.html", "Editar Usuario", "usuarios", usuario=usuario)


@app.route("/usuarios/eliminar/<int:id>", methods=["GET", "POST"])
@rol_requerido("Coordinador")
def usuarios_eliminar(id):
    """Eliminar un usuario (DELETE)."""
    usuario = Usuario.query.get_or_404(id)
    if request.method == "POST":
        try:
            nombre = usuario.nombre
            # SQL: DELETE FROM USUARIO WHERE id=?
            db.session.delete(usuario)
            db.session.commit()
            flash(f"Usuario {nombre} eliminado.", "success")
            return redirect(url_for("usuarios"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")
    return _aplicacion("aplicacion/usuarios/usuarios_delete.html", "Eliminar Usuario", "usuarios", usuario=usuario)


# =============================================================================
# MATERIAS — CRUD completo
# =============================================================================
@app.route("/materias")
@login_requerido
def materias():
    """Lista todas las materias reales desde la BD."""
    materias = Materia.query.all()
    return _aplicacion("aplicacion/materias.html", "Materias", "materias", materias=materias)


@app.route("/materias/crear", methods=["GET", "POST"])
@rol_requerido("Coordinador", "Profesor")
def materias_crear():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        periodo_id = request.form.get("periodo_id")

        if nombre and periodo_id:
            try:
                periodo = PeriodoAcademico.query.get(int(periodo_id))
                if not periodo:
                    flash("Periodo no válido.", "danger")
                else:
                    # Instancia POO + INSERT
                    nueva = Materia(nombre=nombre, descripcion=descripcion, periodo=periodo)
                    db.session.add(nueva)
                    db.session.commit()
                    flash(f"Materia {nombre} creada.", "success")
                    return redirect(url_for("materias"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
        else:
            flash("Nombre y período son obligatorios.", "danger")

    periodos = PeriodoAcademico.query.all()
    return _aplicacion(
        "aplicacion/formularios/crear_materia.html", "Crear Materia", "materias",
        periodos=periodos,
    )


@app.route("/materias/editar/<int:id>", methods=["GET", "POST"])
@rol_requerido("Coordinador", "Profesor")
def materias_editar(id):
    materia = Materia.query.get_or_404(id)
    if request.method == "POST":
        try:
            materia.nombre = request.form.get("nombre", materia.nombre)
            materia.descripcion = request.form.get("descripcion", materia.descripcion)
            # SQL: UPDATE MATERIA SET ... WHERE id=?
            db.session.commit()
            flash("Materia actualizada.", "success")
            return redirect(url_for("materias"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")
    return _aplicacion("aplicacion/materias_edit.html", "Editar Materia", "materias", materia=materia)


@app.route("/materias/eliminar/<int:id>", methods=["POST"])
@rol_requerido("Coordinador")
def materias_eliminar(id):
    materia = Materia.query.get_or_404(id)
    try:
        nombre = materia.nombre
        # SQL: DELETE FROM MATERIA WHERE id=?
        db.session.delete(materia)
        db.session.commit()
        flash(f"Materia {nombre} eliminada.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("materias"))


# =============================================================================
# TAREAS — CRUD con login
# =============================================================================
@app.route("/tareas")
@login_requerido
def tareas():
    rol = session.get("rol")
    if rol == "Estudiante":
        # SQL con JOIN: tareas donde el estudiante tiene entregas
        tareas = Tarea.query.join(Entrega).filter(
            Entrega.estudiante_id == session["user_id"]
        ).all()
    else:
        # SQL: SELECT * FROM TAREA
        tareas = Tarea.query.all()
    return _aplicacion("aplicacion/usuarios/tareas.html", "Tareas", "tareas", tareas=tareas)


@app.route("/tareas/crear", methods=["GET", "POST"])
@rol_requerido("Profesor", "Coordinador")
def tareas_crear():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        instrucciones = request.form.get("instrucciones", "").strip()
        fecha_limite = request.form.get("fecha_limite", "").strip()
        materia_id = request.form.get("materia_id")

        if titulo and fecha_limite and materia_id:
            try:
                materia = Materia.query.get(int(materia_id))
                profesor = Usuario.query.get(session["user_id"])
                # Instancia POO + INSERT
                nueva = Tarea(
                    titulo=titulo, instrucciones=instrucciones,
                    fecha_limite=fecha_limite, materia=materia, creadoPor=profesor,
                )
                db.session.add(nueva)
                db.session.commit()
                flash(f"Tarea '{titulo}' creada.", "success")
                return redirect(url_for("tareas"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
        else:
            flash("Título, fecha límite y materia son obligatorios.", "danger")

    materias = Materia.query.all()
    return _aplicacion(
        "aplicacion/formularios/crear_tarea.html", "Crear Tarea", "tareas",
        materias=materias,
    )


@app.route("/tareas/eliminar/<int:id>", methods=["POST"])
@rol_requerido("Profesor", "Coordinador")
def tareas_eliminar(id):
    tarea = Tarea.query.get_or_404(id)
    try:
        titulo = tarea.titulo
        # SQL: DELETE FROM TAREA WHERE id=?
        db.session.delete(tarea)
        db.session.commit()
        flash(f"Tarea '{titulo}' eliminada.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("tareas"))


@app.route("/entregas/crear/<int:tarea_id>", methods=["POST"])
@rol_requerido("Estudiante")
def entregas_crear(tarea_id):
    """Estudiante entrega una tarea (método POO Estudiante.entregarTarea)."""
    archivo_url = request.form.get("archivo_url", "").strip()
    try:
        tarea = Tarea.query.get_or_404(tarea_id)
        estudiante = Usuario.query.get(session["user_id"])
        # Método POO: encapsula INSERT en ENTREGA
        if isinstance(estudiante, Estudiante):
            estudiante.entregarTarea(tarea, archivo_url)
        else:
            # Fallback si el usuario no se cargó como Estudiante
            nueva = Entrega(
                tarea_id=tarea_id, estudiante_id=estudiante.id,
                archivo_url=archivo_url, fecha_entrega=datetime.now(),
                estado="Entregado",
            )
            db.session.add(nueva)
            db.session.commit()
        flash("Tarea entregada.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("tareas"))


# =============================================================================
# COMUNICADOS — método POO publicar()
# =============================================================================
@app.route("/comunicados")
@login_requerido
def comunicados():
    """Lista comunicados reales activos desde la BD."""
    comunicados = Comunicado.query.filter_by(activo=True)\
        .order_by(Comunicado.publicado_en.desc()).all()
    return _aplicacion("aplicacion/comunicados.html", "Comunicados", "comunicados", comunicados=comunicados)


@app.route("/comunicados/publicar", methods=["GET", "POST"])
@rol_requerido("Coordinador")
def comunicados_publicar():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()

        if titulo and contenido:
            try:
                coordinador = Usuario.query.get(session["user_id"])
                # Instancia POO
                com = Comunicado(
                    titulo=titulo, contenido=contenido,
                    creadoPor=coordinador, publicadoEn=datetime.now(), activo=True,
                )
                # Método POO encapsulado
                com.publicarComunicado()
                flash("Comunicado publicado.", "success")
                return redirect(url_for("comunicados"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
        else:
            flash("Título y contenido son obligatorios.", "danger")

    return _aplicacion("aplicacion/comunicados_publicar.html", "Publicar Comunicado", "comunicados")


@app.route("/comunicados/eliminar/<int:id>", methods=["POST"])
@rol_requerido("Coordinador")
def comunicados_eliminar(id):
    """Desactivar un comunicado (UPDATE activo=0)."""
    com = Comunicado.query.get_or_404(id)
    try:
        com.activo = False
        # SQL: UPDATE COMUNICADO SET activo=0 WHERE id=?
        db.session.commit()
        flash("Comunicado desactivado.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("comunicados"))


# =============================================================================
# MENSAJERÍA — método POO enviarMensaje()
# =============================================================================
@app.route("/mensajeria")
@login_requerido
def mensajeria():
    """Lista los mensajes del usuario en sesión (recibidos)."""
    usuario_id = session["user_id"]
    mensajes = Mensaje.query.filter_by(destinatario_id=usuario_id)\
        .order_by(Mensaje.enviado_en.desc()).all()
    return _aplicacion("aplicacion/usuarios/mensajeria.html", "Mensajería", "mensajeria", mensajes=mensajes)


@app.route("/mensajeria/enviar", methods=["GET", "POST"])
@login_requerido
def mensajeria_enviar():
    """
    Enviar mensaje real (INSERT INTO MENSAJE).
    Usa el método POO Mensaje.enviarMensaje().
    """
    if request.method == "POST":
        destinatario_id = request.form.get("destinatario_id")
        asunto = request.form.get("asunto", "").strip()
        cuerpo = request.form.get("cuerpo", "").strip()

        if destinatario_id and asunto and cuerpo:
            try:
                remitente = Usuario.query.get(session["user_id"])
                destinatario = Usuario.query.get(int(destinatario_id))
                # Instancia POO
                m = Mensaje(
                    remitente=remitente, destinatario=destinatario,
                    asunto=asunto, cuerpo=cuerpo,
                )
                # Método POO encapsulado
                m.enviarMensaje()
                flash("Mensaje enviado.", "success")
                return redirect(url_for("mensajeria"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
        else:
            flash("Destinatario, asunto y cuerpo son obligatorios.", "danger")

    usuarios = Usuario.query.filter(Usuario.id != session["user_id"]).all()
    return _aplicacion(
        "aplicacion/mensajeria_enviar.html", "Enviar Mensaje", "mensajeria",
        usuarios=usuarios,
    )


@app.route("/mensajeria/leer/<int:id>", methods=["POST"])
@login_requerido
def mensajeria_leer(id):
    """Marcar mensaje como leído (método POO Mensaje.leerMensaje)."""
    msg = Mensaje.query.get_or_404(id)
    if msg.destinatario_id != session["user_id"]:
        flash("No tienes permiso para este mensaje.", "danger")
    else:
        try:
            # Método POO encapsulado
            msg.leerMensaje()
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")
    return redirect(url_for("mensajeria"))


# =============================================================================
# CRONOGRAMA — CRUD
# =============================================================================
@app.route("/cronograma")
@login_requerido
def cronograma():
    """Lista eventos reales del cronograma."""
    eventos = Cronograma.query.order_by(Cronograma.fecha_evento.asc()).all()
    return _aplicacion("aplicacion/usuarios/cronograma.html", "Cronograma", "cronograma", eventos=eventos)


@app.route("/cronograma/crear", methods=["GET", "POST"])
@rol_requerido("Coordinador", "Profesor")
def cronograma_crear():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        fecha_evento = request.form.get("fecha_evento", "").strip()
        tipo = request.form.get("tipo", "").strip() or None
        materia_id = request.form.get("materia_id")

        if titulo and fecha_evento and materia_id:
            try:
                materia = Materia.query.get(int(materia_id))
                creador = Usuario.query.get(session["user_id"])
                ev = Cronograma(
                    titulo=titulo, descripcion=descripcion,
                    fecha_evento=fecha_evento, tipo=tipo,
                    materia=materia, creadoPor=creador,
                )
                db.session.add(ev)
                db.session.commit()
                flash("Evento agregado.", "success")
                return redirect(url_for("cronograma"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
        else:
            flash("Título, fecha y materia son obligatorios.", "danger")

    materias = Materia.query.all()
    return _aplicacion(
        "aplicacion/cronograma_crear.html", "Crear Evento", "cronograma",
        materias=materias,
    )


@app.route("/cronograma/eliminar/<int:id>", methods=["POST"])
@rol_requerido("Coordinador", "Profesor")
def cronograma_eliminar(id):
    ev = Cronograma.query.get_or_404(id)
    try:
        db.session.delete(ev)
        db.session.commit()
        flash("Evento eliminado.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("cronograma"))


# =============================================================================
# RECURSOS — CRUD
# =============================================================================
@app.route("/recursos")
@login_requerido
def recursos():
    """Lista recursos reales desde la BD."""
    recursos = Recurso.query.all()
    return _aplicacion("aplicacion/recursos/recursos.html", "Recursos", "recursos", recursos=recursos)


@app.route("/recursos/crear", methods=["GET", "POST"])
@rol_requerido("Coordinador", "Profesor")
def recursos_crear():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        url_archivo = request.form.get("url_archivo", "").strip()
        tipo = request.form.get("tipo", "").strip() or None
        materia_id = request.form.get("materia_id")

        if titulo and materia_id:
            try:
                materia = Materia.query.get(int(materia_id))
                creador = Usuario.query.get(session["user_id"])
                rec = Recurso(
                    titulo=titulo, descripcion=descripcion,
                    urlArchivo=url_archivo, tipo=tipo,
                    materia=materia, creadoPor=creador,
                )
                db.session.add(rec)
                db.session.commit()
                flash("Recurso creado.", "success")
                return redirect(url_for("recursos"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
        else:
            flash("Título y materia son obligatorios.", "danger")

    materias = Materia.query.all()
    return _aplicacion(
        "aplicacion/formularios/crear_recurso.html", "Subir Recurso", "recursos",
        materias=materias,
    )


@app.route("/recursos/eliminar/<int:id>", methods=["POST"])
@rol_requerido("Coordinador", "Profesor")
def recursos_eliminar(id):
    rec = Recurso.query.get_or_404(id)
    try:
        db.session.delete(rec)
        db.session.commit()
        flash("Recurso eliminado.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("recursos"))


# =============================================================================
# GRUPOS — CRUD
# =============================================================================
@app.route("/grupos")
@login_requerido
def grupos():
    """Lista grupos reales desde la BD."""
    grupos = Grupo.query.all()
    return _aplicacion("aplicacion/grupos/grupos.html", "Grupos", "grupos", grupos=grupos)


@app.route("/grupos/crear", methods=["GET", "POST"])
@rol_requerido("Coordinador", "Profesor")
def grupos_crear():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        materia_id = request.form.get("materia_id")

        if nombre and materia_id:
            try:
                materia = Materia.query.get(int(materia_id))
                creador = Usuario.query.get(session["user_id"])
                # Instancia POO + INSERT
                g = Grupo(
                    nombre=nombre, descripcion=descripcion,
                    materia=materia, creadoPor=creador,
                )
                db.session.add(g)
                db.session.commit()
                flash("Grupo creado.", "success")
                return redirect(url_for("grupos"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
        else:
            flash("Nombre y materia son obligatorios.", "danger")

    materias = Materia.query.all()
    return _aplicacion(
        "aplicacion/formularios/crear_grupo.html", "Crear Grupo", "grupos",
        materias=materias,
    )


# =============================================================================
# PERÍODOS — CRUD
# =============================================================================
@app.route("/periodos")
@rol_requerido("Coordinador")
def periodos():
    periodos = PeriodoAcademico.query.all()
    return _aplicacion("aplicacion/periodos.html", "Períodos", "configuracion", periodos=periodos)


@app.route("/periodos/crear", methods=["GET", "POST"])
@rol_requerido("Coordinador")
def periodos_crear():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        fecha_inicio = request.form.get("fecha_inicio", "").strip()
        fecha_fin = request.form.get("fecha_fin", "").strip()

        if nombre and fecha_inicio and fecha_fin:
            try:
                p = PeriodoAcademico(
                    nombre=nombre, fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin, activo=True,
                )
                db.session.add(p)
                db.session.commit()
                flash("Período creado.", "success")
                return redirect(url_for("periodos"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
        else:
            flash("Todos los campos son obligatorios.", "danger")

    return _aplicacion("aplicacion/formularios/crear_periodo.html", "Crear Período", "configuracion")


# =============================================================================
# INFORMES Y CONFIGURACIÓN
# =============================================================================
@app.route("/informacion")
@login_requerido
def informacion():
    return _aplicacion("aplicacion/informacion/informacion.html", "Información", "informacion")


@app.route("/reportes")
@rol_requerido("Coordinador", "Profesor")
def reportes():
    """Reportes: estadísticas reales desde la BD."""
    stats = {
        "total_usuarios": Usuario.query.count(),
        "total_estudiantes": Usuario.query.filter_by(rol="Estudiante").count(),
        "total_profesores": Usuario.query.filter_by(rol="Profesor").count(),
        "total_coordinadores": Usuario.query.filter_by(rol="Coordinador").count(),
        "total_materias": Materia.query.count(),
        "total_tareas": Tarea.query.count(),
        "total_entregas": Entrega.query.count(),
        "total_comunicados": Comunicado.query.count(),
        "total_mensajes": Mensaje.query.count(),
    }
    return _aplicacion("aplicacion/reportes/reportes.html", "Reportes", "reportes", stats=stats)


@app.route("/configuracion")
@login_requerido
def configuracion():
    return _aplicacion("aplicacion/config/configuracion.html", "Configuración", "configuracion")


# =============================================================================
# RUTAS PÚBLICAS
# =============================================================================
@app.route("/programa-pop")
def programa_pop():
    return _pagina("pagina/ProgramaPOP.html", "Programa POP", "programa-pop")


@app.route("/Estructura")
def estructura():
    return _pagina("pagina/estructura.html", "Estructura", "estructura")


@app.route("/ques")
def ques():
    return _pagina("pagina/QUES.html", "¿Qué es ZOE?", "ques")


# =============================================================================
# HEALTH CHECK
# =============================================================================
@app.route("/health")
def health():
    return {"status": "ok", "app": "ZOE"}, 200


# =============================================================================
# Inicialización de la base de datos
# =============================================================================
def init_db():
    """Crea la BD y las tablas si no existen."""
    from sqlalchemy import create_engine

    with app.app_context():
        db_name = "zoe"
        server_uri = "mysql+pymysql://root:@localhost"
        server_engine = create_engine(server_uri)
        try:
            with server_engine.connect() as conn:
                conn.execute(db.text(f"DROP DATABASE IF EXISTS `{db_name}`"))
                conn.commit()
                conn.execute(db.text(
                    f"CREATE DATABASE `{db_name}` "
                    f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                ))
                conn.commit()
                print(f"-> Base de datos `{db_name}` creada")
            server_engine.dispose()
        except Exception as e:
            print(f"ERROR al crear la BD: {e}")
            return False

        try:
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))
            db.create_all()
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
            db.session.commit()
            print("OK - Tablas creadas con InnoDB")
        except Exception as e:
            print(f"ERROR al crear tablas: {e}")
            return False
    return True


# =============================================================================
# Flask-Migrate: alternativa a init_db() para manejar cambios de esquema.
# Uso:
#   export FLASK_APP=main.py   (Linux/Mac)
#   set FLASK_APP=main.py      (Windows)
#   flask db init
#   flask db migrate -m "mensaje"
#   flask db upgrade
# =============================================================================
try:
    from flask_migrate import Migrate
    migrate = Migrate(app, db)
except ImportError:
    migrate = None

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)


