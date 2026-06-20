"""
ZOE - Plataforma de Gestión Documental para el IB
Application Factory Pattern
"""

from flask import Flask, session
from datetime import datetime

from app.config_db import config, db
from app.blueprints import (
    auth_bp, dashboard_bp, tareas_bp, materias_bp, grupos_bp,
    comunicados_bp, recursos_bp, cronograma_bp, mensajeria_bp,
    reportes_bp, configuracion_bp, usuarios_bp
)


def create_app(config_name="development"):
    """
    Factory function para crear la aplicación Flask.
    
    Args:
        config_name: Nombre de la configuración ('development', 'production', 'default')
    
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Variables globales para templates Jinja2
    @app.context_processor
    def variables_globales():
        return {
            "app_name": "ZOE IB",
            "usuario_id": session.get("usuario_id"),
            "usuario": session.get("usuario", "Usuario Demo"),
            "rol": session.get("rol", "invitado"),
        }
    
    # Registrar blueprints con sus prefijos de URL
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(tareas_bp, url_prefix='/tareas')
    app.register_blueprint(materias_bp, url_prefix='/materias')
    app.register_blueprint(grupos_bp, url_prefix='/grupos')
    app.register_blueprint(comunicados_bp, url_prefix='/comunicados')
    app.register_blueprint(recursos_bp, url_prefix='/recursos')
    app.register_blueprint(cronograma_bp, url_prefix='/cronograma')
    app.register_blueprint(mensajeria_bp, url_prefix='/mensajeria')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    app.register_blueprint(configuracion_bp, url_prefix='/configuracion')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    
    # Ruta pública de inicio
    @app.route("/")
    def inicio():
        from flask import render_template
        return render_template("pagina/index.html", page_title="Inicio", active_page="index")
    
    # Rutas públicas de información
    @app.route("/ques")
    def ques():
        from flask import render_template
        return render_template("pagina/QUES.html", page_title="¿Qué es ZOE?", active_page="ques")
    
    @app.route("/programa-pop")
    def programa_pop():
        from flask import render_template
        return render_template("pagina/ProgramaPOP.html", page_title="Programa POP", active_page="programa-pop")
    
    @app.route("/estructura")
    def estructura():
        from flask import render_template
        return render_template("pagina/estructura.html", page_title="Estructura Académica", active_page="estructura")
    
    # Ruta de health check
    @app.route("/health")
    def health():
        return {"status": "ok", "app": "ZOE"}, 200
    
    return app