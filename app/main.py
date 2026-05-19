"""
Aplicación web ZOE — punto de entrada.

Todas las rutas se definen aquí con @app.route.
Configuración en config.py.
"""

import sys
from pathlib import Path

from flask import Flask, render_template

from config import Config

# -----------------------------------------------------------------------------
# Rutas del proyecto (para importar modelo/ y controlador/ más adelante)
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent       # ZOE_APP/app/
PROJECT_ROOT = BASE_DIR.parent                 # ZOE_APP/

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
    """
    Datos disponibles en cualquier HTML sin repetirlos en cada ruta.

    Uso futuro en plantillas: {{ app_name }}, {{ usuario_id }}
    """
    return {
        "app_name": "ZOE IB",
        # "usuario_id": session.get("user_id"),       # login futuro
        # "ia_disponible": bool(app.config["AI_API_KEY"]),
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


# -----------------------------------------------------------------------------
# Rutas de páginas (templates/pagina/)
# -----------------------------------------------------------------------------
@app.route("/")
def inicio():
    return _pagina("pagina/index.html", "Inicio", "index")


@app.route("/coordinacion")
def coordinacion():
    return _pagina("pagina/coordinacion.html", "Coordinación", "coordinacion")


@app.route("/institucion")
def institucion():
    return _pagina("pagina/institucion.html", "Institución", "institucion")


@app.route("/material")
def material():
    return _pagina("pagina/material.html", "Material", "material")


@app.route("/materias")
def materias():
    return _pagina("pagina/materias.html", "Materias", "materias")


@app.route("/orientacion")
def orientacion():
    # El archivo en disco se llama Orientacion.html (O mayúscula)
    return _pagina("pagina/Orientacion.html", "Orientación", "orientacion")


# -----------------------------------------------------------------------------
# Rutas futuras (descomentar cuando las implementes)
# -----------------------------------------------------------------------------
# from flask import request, redirect, url_for, session
#
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         # Validar usuario con modelo/ + lógica en controlador/
#         # session["user_id"] = usuario.get_id()
#         # return redirect(url_for("inicio"))
#         pass
#     return render_template("aplicacion/login.html")
#
#
# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("inicio"))


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
    # Ejecutar desde ZOE_APP/app/:
    #   python main.py
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)
