"""
Rutas del blueprint de Reportes.
Maneja la generación de reportes.
"""

from flask import render_template

from app.blueprints import reportes_bp


@reportes_bp.route('/')
def reportes():
    """Página de reportes."""
    return render_template(
        'aplicacion/reportes/reportes.html',
        page_title='Reportes',
        active_page='reportes'
    )