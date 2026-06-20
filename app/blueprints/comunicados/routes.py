"""
Rutas del blueprint de Comunicados.
Maneja la visualización de comunicados y anuncios.
"""

from flask import render_template

from app.blueprints import comunicados_bp
from app.models import Comunicado


@comunicados_bp.route('/')
def listar_comunicados():
    """Lista todos los comunicados activos."""
    comunicados = Comunicado.obtener_activos()
    return render_template(
        'aplicacion/informacion/informacion.html',
        page_title='Información',
        active_page='informacion',
        comunicados=comunicados
    )