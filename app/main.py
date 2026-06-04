"""
Aplicación web ZOE — punto de entrada.

Todas las rutas se definen aquí con @app.route.
Configuración en config.py.
"""

import sys
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

from config import Config

# -----------------------------------------------------------------------------
# Rutas del proyecto (para importar modelo/ y controlador/ más adelante)
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent       # ZOE_APP/app/
PROJECT_ROOT = BASE_DIR.parent                  # ZOE_APP/

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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


# -----------------------------------------------------------------------------
# Variables globales para todos los templates (Jinja2)
# -----------------------------------------------------------------------------
@app.context_processor
def variables_globales():
    return {
        "app_name": "ZOE IB",
        # "usuario_id": session.get("user_id"),       # login futuro
    }


# -----------------------------------------------------------------------------
# Helper interno — reduce repetición al renderizar páginas
# -----------------------------------------------------------------------------
def _pagina(template, titulo, pagina_activa):
    return render_template(
        template,
        page_title=titulo,
        active_page=pagina_activa,
    )
    
def _aplicacion(template, titulo, pagina_activa, **kwargs):
    return render_template(
        template,
        page_title=titulo,
        active_page=pagina_activa,
        **kwargs
    )



# -----------------------------------------------------------------------------
# Rutas de páginas públicas (templates/pagina/)
# -----------------------------------------------------------------------------
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




# -----------------------------------------------------------------------------
# Rutas de aplicación interna (templates/aplicacion/)
# -----------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Simulación: siempre entra como estudiante
        session["usuario"] = request.form["email"]
        session["rol"] = "estudiante"
        return ("/dashboard")
    # Renderiza la plantilla de login
    return _aplicacion("aplicacion/auth/login.html", "Login", "login")

@app.route("/dashboard")
def dashboard():
    rol = session.get("rol", "estudiante")   # valor por defecto
    usuario = session.get("usuario", "Usuario Demo")
    fecha = "martes, 2 de junio de 2026"

    return _aplicacion("aplicacion/dashboard.html", "Dashboard", "dashboard",usuario=usuario, rol=rol, fecha=fecha)

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

@app.route("/grupos")
def grupos():
    return _aplicacion("aplicacion/grupos/grupos.html", "Grupos", "grupos")

@app.route("/configuracion")
def configuracion():
    return _aplicacion("aplicacion/config/configuracion.html", "Configuración", "configuracion")


# -----------------------------------------------------------------------------
# Rutas de gestión de usuarios (CRUD)
# -----------------------------------------------------------------------------
@app.route("/usuarios")
def usuarios_list():
    return _aplicacion("aplicacion/usuarios/usuarios.html", "Usuarios", "usuarios")

@app.route("/usuarios/crear")
def usuarios_create():
    return _aplicacion("aplicacion/usuarios/usuarios_create.html", "Crear Usuario", "usuarios")

@app.route("/usuarios/editar/<int:id>")
def usuarios_edit(id):
    return _aplicacion("aplicacion/usuarios/usuarios_edit.html", "Editar Usuario", "usuarios")

@app.route("/usuarios/eliminar/<int:id>")
def usuarios_delete(id):
    return _aplicacion("aplicacion/usuarios/usuarios_delete.html", "Eliminar Usuario", "usuarios")


# -----------------------------------------------------------------------------
# Comprobación rápida de que el servidor responde
# -----------------------------------------------------------------------------
@app.route("/health")
def health():
    return {"status": "ok", "app": "ZOE"}, 200


# -----------------------------------------------------------------------------
# Arranque en desarrollo
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)
