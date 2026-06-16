"""
ZOE - Plataforma de Gestión Documental para el IB
"""

from flask import Flask
from app.models import db


def create_app(config_name="development"):
    """Factory function para crear la aplicación Flask."""
    from app.config_db import config
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar SQLAlchemy
    db.init_app(app)
    
    return app
