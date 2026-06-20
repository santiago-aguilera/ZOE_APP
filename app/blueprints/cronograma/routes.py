"""
Rutas del blueprint de Cronograma.
Maneja la visualización del calendario de eventos.
"""

from flask import render_template

from app.blueprints import cronograma_bp
from app.models import Cronograma


@cronograma_bp.route('/')
def listar_cronograma():
    """Lista todos los eventos del cronograma."""
    eventos = Cronograma.obtener_todos()
    return render_template(
        'aplicacion/cronograma.html',
        page_title='Cronograma',
        active_page='cronograma',
        eventos=eventos
    )