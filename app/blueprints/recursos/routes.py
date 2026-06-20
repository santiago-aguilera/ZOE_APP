"""
Rutas del blueprint de Recursos.
Maneja la visualización de recursos educativos.
"""

from flask import render_template

from app.blueprints import recursos_bp
from app.models import Recurso


@recursos_bp.route('/')
def listar_recursos():
    """Lista todos los recursos."""
    recursos = Recurso.obtener_todos()
    return render_template(
        'aplicacion/recursos/recursos.html',
        page_title='Recursos Académicos',
        active_page='recursos',
        recursos=recursos
    )