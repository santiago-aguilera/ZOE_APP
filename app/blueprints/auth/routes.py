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
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Buscar usuario en la BD
        usuario = Usuario.obtener_por_correo(email)
        
        if usuario and check_password_hash(usuario.contrasena_hash, password):
            # Guardar en sesión
            session['usuario_id'] = usuario.id
            session['usuario'] = usuario.nombre
            session['correo'] = usuario.correo
            session['rol'] = usuario.rol
            session.permanent = True
            
            flash(f'Bienvenido, {usuario.nombre}', 'success')
            return redirect(url_for('dashboard'))
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