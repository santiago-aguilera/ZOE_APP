"""
ZOE — Inicialización de la aplicación Flask con SQLAlchemy.
Factory pattern para permitir pruebas y seed_data.
"""

from flask import Flask
from config import Config
from models import db


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder=str(Config.TEMPLATES_FOLDER),
        static_folder=str(Config.STATIC_FOLDER),
        static_url_path="/static",
    )
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        from models import (
            PeriodoAcademico, Usuario, Materia, ProfesorMateria,
            EstudianteMateria, Tarea, Entrega, Cronograma,
            Mensaje, Recurso, Comunicado, Grupo, EstudianteGrupo
        )

        # Importar y registrar rutas
        from main import register_routes
        register_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)