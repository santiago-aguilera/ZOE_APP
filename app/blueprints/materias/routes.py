"""
Rutas del blueprint de Materias.
Maneja la visualización de materias.
"""

from flask import render_template

from app.blueprints import materias_bp
from app.models import Materia


@materias_bp.route('/')
def listar_materias():
    """Lista todas las materias."""
    materias = Materia.obtener_todas()
    return render_template(
        'aplicacion/materias.html',
        page_title='Materias',
        active_page='materias',
        materias=materias
    )