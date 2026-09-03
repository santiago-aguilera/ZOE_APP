"""
Rutas del blueprint de Autenticación.
Maneja login, logout y autenticación de usuarios.
"""

from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

from app.blueprints import auth_bp
from app.models import Usuario


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuarios."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        # Los espacios pueden ser parte de una contraseÃ±a vÃ¡lida.
        password = request.form.get('password', '')
        
        # Buscar usuario en la BD
        usuario = Usuario.obtener_por_correo(email)
        
        password_valida = False
        if usuario and usuario.activo and usuario.contrasena_hash:
            try:
                password_valida = check_password_hash(usuario.contrasena_hash, password)
            except (TypeError, ValueError):
                # Un hash corrupto no debe terminar en un error 500.
                password_valida = False

        if password_valida:
            # Guardar en sesión
            session['usuario_id'] = usuario.id
            session['usuario'] = usuario.nombre
            session['correo'] = usuario.correo
            session['rol'] = usuario.rol
            session.permanent = request.form.get('remember') == 'on'
            
            flash(f'Bienvenido, {usuario.nombre}', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Credenciales inválidas. Por favor, intenta de nuevo.', 'error')
    
    return render_template(
        'aplicacion/auth/login.html',
        page_title='Login',
        active_page='login'
    )


@auth_bp.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('inicio'))
