"""
Rutas del blueprint de Usuarios.
Maneja la gestión de usuarios del sistema.
"""

from flask import render_template

from app.blueprints import usuarios_bp
from app.models import Usuario


@usuarios_bp.route('/')
def listar_usuarios():
    """Lista todos los usuarios del sistema."""
    usuarios = Usuario.obtener_todos()
    return render_template(
        'aplicacion/usuarios/usuarios.html',
        page_title='Usuarios',
        active_page='usuarios',
        usuarios=usuarios
    )