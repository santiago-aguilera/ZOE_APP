"""
Rutas del blueprint de Configuración.
Maneja la configuración del sistema.
"""

from flask import render_template

from app.blueprints import configuracion_bp


@configuracion_bp.route('/')
def configuracion():
    """Página de configuración."""
    return render_template(
        'aplicacion/config/configuracion.html',
        page_title='Configuración',
        active_page='configuracion'
    )