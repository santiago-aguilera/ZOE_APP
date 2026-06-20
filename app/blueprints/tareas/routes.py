"""
Rutas del blueprint de Tareas.
Maneja la visualización y gestión de tareas.
"""

from flask import render_template

from app.blueprints import tareas_bp
from app.models import Tarea


@tareas_bp.route('/')
def listar_tareas():
    """Lista todas las tareas."""
    tareas = Tarea.obtener_todas()
    return render_template(
        'aplicacion/tareas.html',
        page_title='Tareas',
        active_page='tareas',
        tareas=tareas
    )