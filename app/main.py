"""
ZOE — Rutas de la aplicación.
Se exporta register_routes() para ser usado desde __init__.py (factory pattern).
"""

import sys
from pathlib import Path
from flask import redirect, render_template, request, session, url_for
from config import Config

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _pagina(template, titulo, pagina_activa):
    return render_template(template, page_title=titulo, active_page=pagina_activa)


def _aplicacion(template, titulo, pagina_activa, **kwargs):
    defaults = {
        "rol": session.get("rol", "estudiante"),
        "usuario": session.get("usuario", "Usuario Demo"),
    }
    defaults.update(kwargs)
    return render_template(template, page_title=titulo, active_page=pagina_activa, **defaults)


def register_routes(app):
    """Registra todas las rutas en la aplicación Flask."""

    @app.context_processor
    def variables_globales():
        return {"app_name": "ZOE IB"}

    # -------------------------------------------------------------------------
    # Páginas públicas (templates/pagina/)
    # -------------------------------------------------------------------------
    @app.route("/")
    def inicio():
        return _pagina("pagina/index.html", "Inicio", "index")

    @app.route("/programa-pop")
    def programa_pop():
        return _pagina("pagina/ProgramaPOP.html", "Programa POP", "programa-pop")

    @app.route("/Estructura")
    def estructura():
        return _pagina("pagina/estructura.html", "Estructura", "estructura")

    @app.route("/ques")
    def ques():
        return _pagina("pagina/QUES.html", "¿Qué es ZOE?", "ques")

    # -------------------------------------------------------------------------
    # Aplicación interna (templates/aplicacion/)
    # -------------------------------------------------------------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "")
            if "coord" in email:
                session["rol"] = "coordinador"
            elif "prof" in email or "lic" in email:
                session["rol"] = "profesor"
            else:
                session["rol"] = "estudiante"
            session["usuario"] = email
            return redirect(url_for("dashboard"))
        return _aplicacion("aplicacion/auth/login.html", "Login", "login")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("inicio"))

    @app.route("/dashboard")
    def dashboard():
        return _aplicacion("aplicacion/dashboard.html", "Dashboard", "dashboard",
                          fecha="martes, 2 de junio de 2026")

    @app.route("/tareas")
    def tareas():
        return _aplicacion("aplicacion/usuarios/tareas.html", "Tareas", "tareas")

    @app.route("/mensajeria")
    def mensajeria():
        return _aplicacion("aplicacion/usuarios/mensajeria.html", "Mensajería", "mensajeria")

    @app.route("/cronograma")
    def cronograma():
        return _aplicacion("aplicacion/usuarios/cronograma.html", "Cronograma", "cronograma")

    @app.route("/recursos")
    def recursos():
        return _aplicacion("aplicacion/recursos/recursos.html", "Recursos Académicos", "recursos")

    @app.route("/informacion")
    def informacion():
        return _aplicacion("aplicacion/informacion/informacion.html", "Información", "informacion")

    @app.route("/reportes")
    def reportes():
        return _aplicacion("aplicacion/reportes/reportes.html", "Reportes", "reportes")

    @app.route("/materias")
    def materias():
        return _aplicacion("aplicacion/materias.html", "Materias", "materias")

    @app.route("/grupos")
    def grupos():
        return _aplicacion("aplicacion/grupos/grupos.html", "Grupos", "grupos")

    @app.route("/configuracion")
    def configuracion():
        return _aplicacion("aplicacion/config/configuracion.html", "Configuración", "configuracion")

    # -------------------------------------------------------------------------
    # Formularios CRUD
    # -------------------------------------------------------------------------
    @app.route("/formularios/crear-usuario")
    def form_crear_usuario():
        return _aplicacion("aplicacion/formularios/crear_usuario.html", "Crear Usuario", "usuarios")

    @app.route("/formularios/crear-materia")
    def form_crear_materia():
        return _aplicacion("aplicacion/formularios/crear_materia.html", "Crear Materia", "configuracion")

    @app.route("/formularios/crear-grupo")
    def form_crear_grupo():
        return _aplicacion("aplicacion/formularios/crear_grupo.html", "Crear Grupo", "configuracion")

    @app.route("/formularios/crear-tarea")
    def form_crear_tarea():
        return _aplicacion("aplicacion/formularios/crear_tarea.html", "Crear Tarea", "tareas")

    @app.route("/formularios/crear-recurso")
    def form_crear_recurso():
        return _aplicacion("aplicacion/formularios/crear_recurso.html", "Subir Recurso", "recursos")

    @app.route("/formularios/crear-periodo")
    def form_crear_periodo():
        return _aplicacion("aplicacion/formularios/crear_periodo.html", "Crear Período", "configuracion")

    # -------------------------------------------------------------------------
    # Gestión de usuarios
    # -------------------------------------------------------------------------
    @app.route("/usuarios")
    def usuarios_list():
        return _aplicacion("aplicacion/usuarios/usuarios.html", "Usuarios", "usuarios")

    @app.route("/usuarios/crear")
    def usuarios_create():
        return redirect(url_for("form_crear_usuario"))

    @app.route("/usuarios/editar/<int:id>")
    def usuarios_edit(id):
        return _aplicacion("aplicacion/usuarios/usuarios_edit.html", "Editar Usuario", "usuarios")

    @app.route("/usuarios/eliminar/<int:id>")
    def usuarios_delete(id):
        return _aplicacion("aplicacion/usuarios/usuarios_delete.html", "Eliminar Usuario", "usuarios")

    # -------------------------------------------------------------------------
    # Health check
    # -------------------------------------------------------------------------
    @app.route("/health")
    def health():
        return {"status": "ok", "app": "ZOE"}, 200


# Para arranque directo `python main.py` (sin DB)
if __name__ == "__main__":
    from flask import Flask
    _app = Flask(
        __name__,
        template_folder=str(Config.TEMPLATES_FOLDER),
        static_folder=str(Config.STATIC_FOLDER),
        static_url_path="/static",
    )
    _app.config.from_object(Config)
    _app.secret_key = Config.SECRET_KEY
    register_routes(_app)
    _app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)