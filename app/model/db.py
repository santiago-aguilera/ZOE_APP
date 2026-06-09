"""
Instancia compartida de SQLAlchemy para todos los modelos.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()