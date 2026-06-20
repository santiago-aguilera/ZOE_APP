"""
Rutas del blueprint de Grupos.
Maneja la visualización de grupos.
"""

from flask import render_template

from app.blueprints import grupos_bp
from app.models import Grupo


@grupos_bp.route('/')
def listar_grupos():
    """Lista todos los grupos."""
    grupos = Grupo.obtener_todos()
    return render_template(
        'aplicacion/grupos/grupos.html',
        page_title='Grupos',
        active_page='grupos',
        grupos=grupos
    )