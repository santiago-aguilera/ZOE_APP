"""
Configuración de la aplicación ZOE.

Centraliza variables sensibles y prepara extensiones futuras
(base de datos, sesiones, IA) sin complicar el proyecto hoy.
"""

import os
from pathlib import Path

# Carpeta actual: ZOE_APP/app/
APP_DIR = Path(__file__).resolve().parent

# Carpeta del proyecto: ZOE_APP/
PROJECT_ROOT = APP_DIR.parent


class Config:
    """Valores compartidos por la aplicación."""

    # Obligatorio para sesiones Flask y login futuro
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-cambiar-en-produccion")

    # Rutas absolutas a tus carpetas actuales
    TEMPLATES_FOLDER = APP_DIR / "templates"
    STATIC_FOLDER = APP_DIR / "static"

    # Sesiones (login futuro)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600  # segundos (1 hora)

    # Base de datos Oracle (activar cuando conectes BD/)
    # Ejemplo: oracle+oracledb://user:pass@localhost:1521/?service_name=XE
    DATABASE_URL = os.environ.get("DATABASE_URL", "")

    # Integración futura con IA
    AI_API_KEY = os.environ.get("AI_API_KEY", "")
    AI_API_BASE_URL = os.environ.get("AI_API_BASE_URL", "")
    AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o-mini")

    # Desarrollo local
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
