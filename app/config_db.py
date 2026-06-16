# Variables de conexión a la BD ZOE (XAMPP/phpMyAdmin)
# Asegúrate de que XAMPP esté corriendo y la BD 'zoe' exista

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

class Config:
    """Configuración base de la aplicación ZOE."""
    
    # Rutas de carpetas
    APP_DIR = Path(__file__).resolve().parent
    TEMPLATES_FOLDER = APP_DIR / "templates"
    STATIC_FOLDER = APP_DIR / "static"
    
    # Sesiones Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "zoe-desarrollo-cambiar-en-produccion")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Desarrollo
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
    
    # =====================================================================
    # CONFIGURACIÓN DE BASE DE DATOS - XAMPP/MySQL
    # =====================================================================
    
    # Conexión a MySQL (XAMPP por defecto)
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "zoe")
    
    # URL de conexión para SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        if DB_PASSWORD
        else f"mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG  # Mostrar queries en desarrollo


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False


# Seleccionar configuración según ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

