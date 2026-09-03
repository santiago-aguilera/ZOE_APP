"""
Decoradores de autenticación y autorización para ZOE.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from mysql.connector.errors import IntegrityError


def login_required(f):
    """Exige que haya una sesión iniciada."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('usuario_id'):
            flash('Debes iniciar sesión para acceder.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def roles_permitidos(*roles):
    """Exige sesión iniciada Y que el rol esté en la lista permitida.
    Uso: @roles_permitidos('coordinador', 'profesor')
    """
    def decorador(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get('usuario_id'):
                flash('Debes iniciar sesión para acceder.', 'error')
                return redirect(url_for('auth.login'))
            if session.get('rol') not in roles:
                flash('No tienes permisos para acceder a esta sección.', 'error')
                return redirect(url_for('dashboard.dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorador


def eliminacion_segura(f):
    """
    Envuelve una ruta de eliminación: si la base de datos rechaza el DELETE
    porque el registro todavía tiene información relacionada (foreign key),
    muestra un mensaje claro en vez de un error 500 crudo, y redirige de
    vuelta sin dejar nada a medio eliminar (el DELETE nunca llegó a
    ejecutarse: MySQL/MariaDB rechaza la operación completa antes de tocar
    ninguna fila cuando hay una FK que lo impide, así que no hace falta un
    rollback manual aparte).
    Uso: @eliminacion_segura (después de los decoradores de permisos)
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IntegrityError:
            flash(
                'No se puede eliminar: este registro todavía tiene información '
                'relacionada (estudiantes, tareas u otros datos). '
                'Desactivalo en vez de eliminarlo, o quitá primero lo relacionado.',
                'error'
            )
            return redirect(request.referrer or url_for('dashboard.dashboard'))
    return decorated


def modulo_requerido(clave):
    """Exige sesión iniciada Y que el módulo esté activo Y que el rol tenga
    permiso sobre él (ambos configurables desde Parametrización).
    Uso: @modulo_requerido('tareas')
    """
    def decorador(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get('usuario_id'):
                flash('Debes iniciar sesión para acceder.', 'error')
                return redirect(url_for('auth.login'))

            from app.models import ModuloSistema, RolPermiso
            rol = session.get('rol')
            if not ModuloSistema.esta_activo(clave):
                flash('Ese módulo está desactivado por el coordinador.', 'error')
                return redirect(url_for('dashboard.dashboard'))
            if not RolPermiso.tiene_permiso(rol, clave):
                flash('No tienes permisos para acceder a esta sección.', 'error')
                return redirect(url_for('dashboard.dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorador


def accion_requerida(modulo_clave, accion):
    """Exige sesión iniciada Y que el rol tenga la ACCIÓN puntual habilitada
    sobre ese módulo (crear/editar/eliminar/cambiar_estado/asignar/...).
    El coordinador siempre puede todo. Esto protege de verdad el backend:
    aunque alguien oculte el botón en el frontend, sin este permiso la
    petición directa a la URL también se rechaza.
    Uso: @accion_requerida('cursos', 'eliminar')
    """
    def decorador(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get('usuario_id'):
                flash('Debes iniciar sesión para acceder.', 'error')
                return redirect(url_for('auth.login'))

            from app.models import RolPermiso
            rol = session.get('rol')
            if not RolPermiso.tiene_permiso_accion(rol, modulo_clave, accion):
                flash('No tenés permiso para hacer esa acción.', 'error')
                return redirect(url_for('dashboard.dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorador
