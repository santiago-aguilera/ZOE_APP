"""
Rutas del blueprint de Mensajeria.
Soporta mensajes 1 a 1 y mensajes masivos a un grupo completo
(cada estudiante del grupo recibe su propia copia individual).
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.blueprints import mensajeria_bp
from app.models import Mensaje, Usuario, Grupo
from app.decorators import login_required, modulo_requerido, eliminacion_segura


@mensajeria_bp.route('/')
@modulo_requerido('mensajeria')
def listar_mensajes():
    """Lista mensajes recibidos del usuario actual."""
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')
    mensajes_recibidos = Mensaje.obtener_recibidos(usuario_id)

    # Usuarios disponibles para el select de "nuevo mensaje" (todos menos yo mismo)
    todos = Usuario.obtener_todos()
    usuarios_disponibles = [u for u in todos if u.id != usuario_id]

    # Solo profesor/coordinador pueden mandarle un mensaje a un grupo entero
    grupos_disponibles = Grupo.obtener_todos() if rol in ('profesor', 'coordinador') else []

    return render_template(
        'aplicacion/mensajeria.html',
        page_title='Mensajería',
        active_page='mensajeria',
        mensajes_recibidos=mensajes_recibidos,
        usuarios_disponibles=usuarios_disponibles,
        grupos_disponibles=grupos_disponibles
    )


@mensajeria_bp.route('/enviar', methods=['POST'])
@login_required
def chat():
    """Envía un mensaje individual a un usuario puntual."""
    destinatario_id = request.form.get('destinatario_id')
    asunto = request.form.get('asunto')
    cuerpo = request.form.get('cuerpo')

    if not destinatario_id or not asunto or not cuerpo:
        flash('Completá destinatario, asunto y mensaje.', 'error')
        return redirect(url_for('mensajeria.listar_mensajes'))

    mensaje = Mensaje(
        remitente_id=session.get('usuario_id'),
        destinatario_id=destinatario_id,
        asunto=asunto,
        cuerpo=cuerpo
    )
    mensaje.guardar()
    flash('Mensaje enviado.', 'success')
    return redirect(url_for('mensajeria.listar_mensajes'))


@mensajeria_bp.route('/enviar-grupo', methods=['POST'])
@login_required
def enviar_a_grupo():
    """Envía un mensaje a todos los estudiantes de un grupo. Solo profesor/coordinador."""
    if session.get('rol') not in ('profesor', 'coordinador'):
        flash('No tenés permiso para enviar mensajes a un grupo completo.', 'error')
        return redirect(url_for('mensajeria.listar_mensajes'))

    grupo_id = request.form.get('grupo_id')
    asunto = request.form.get('asunto_grupo')
    cuerpo = request.form.get('cuerpo_grupo')

    if not grupo_id or not asunto or not cuerpo:
        flash('Completá el grupo, el asunto y el mensaje.', 'error')
        return redirect(url_for('mensajeria.listar_mensajes'))

    cantidad = Mensaje.enviar_a_grupo(
        remitente_id=session.get('usuario_id'),
        grupo_id=grupo_id,
        asunto=asunto,
        cuerpo=cuerpo
    )

    if cantidad == 0:
        flash('Ese grupo todavía no tiene estudiantes inscritos — no se envió a nadie.', 'error')
    else:
        flash(f'Mensaje enviado a {cantidad} estudiante(s) del grupo.', 'success')

    return redirect(url_for('mensajeria.listar_mensajes'))


@mensajeria_bp.route('/<int:mensaje_id>/marcar-leido', methods=['POST'])
@login_required
def marcar_leido(mensaje_id):
    """Marca un mensaje como leído."""
    Mensaje.marcar_leido(mensaje_id, session.get('usuario_id'))
    return redirect(url_for('mensajeria.listar_mensajes'))


@mensajeria_bp.route('/<int:mensaje_id>/eliminar', methods=['GET','POST'])
@login_required
@eliminacion_segura
def eliminar_mensaje(mensaje_id):
    """Borra el mensaje SOLO de la bandeja del usuario actual (borrado suave)."""
    usuario_id = session.get('usuario_id')
    mensaje = Mensaje.obtener_por_id(mensaje_id)
    if not mensaje:
        flash('Mensaje no encontrado.', 'error')
        return redirect(url_for('mensajeria.listar_mensajes'))

    from app.delete_helpers import listar_dependencias
    if request.method == 'GET':
        dependencias = listar_dependencias('mensaje', mensaje_id)
        return render_template(
            'aplicacion/confirm_delete.html',
            title='Confirmar eliminación de mensaje',
            entidad_nombre=getattr(mensaje, 'asunto', f'Mensaje {mensaje_id}'),
            entidad_id=mensaje_id,
            dependencias=dependencias,
            volver_url=request.referrer or url_for('mensajeria.listar_mensajes')
        )

    Mensaje.eliminar_para_usuario(mensaje_id, usuario_id)
    flash('Mensaje eliminado.', 'success')
    return redirect(url_for('mensajeria.listar_mensajes'))