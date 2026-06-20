"""
Rutas del blueprint de Mensajería.
Maneja el sistema de mensajes internos.
"""

from flask import render_template, session

from app.blueprints import mensajeria_bp
from app.models import Mensaje


@mensajeria_bp.route('/')
def listar_mensajes():
    """Lista mensajes recibidos y enviados del usuario actual."""
    usuario_id = session.get('usuario_id')
    
    mensajes_recibidos = Mensaje.obtener_recibidos(usuario_id)
    
    return render_template(
        'aplicacion/mensajeria.html',
        page_title='Mensajería',
        active_page='mensajeria',
        mensajes_recibidos=mensajes_recibidos
    )