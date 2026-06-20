"""
Rutas del blueprint de Dashboard.
Página principal después del login.
"""

from flask import render_template, session
from datetime import datetime

from app.blueprints import dashboard_bp
from app.models import Usuario, Tarea, Grupo, Materia


@dashboard_bp.route('/')
def dashboard():
    """Dashboard principal con estadísticas según el rol."""
    usuario_id = session.get('usuario_id')
    usuario = session.get('usuario', 'Usuario Demo')
    rol = session.get('rol', 'estudiante')
    
    # Fecha actual en español
    fecha = datetime.now().strftime("%A, %d de %B de %Y")
    traducciones = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado',
        'Sunday': 'Domingo', 'January': 'enero', 'February': 'febrero',
        'March': 'marzo', 'April': 'abril', 'May': 'mayo', 'June': 'junio',
        'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
        'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    for en, es in traducciones.items():
        fecha = fecha.replace(en, es)
    
    contexto = {
        'usuario': usuario,
        'usuario_id': usuario_id,
        'rol': rol,
        'fecha': fecha,
    }
    
    # Estadísticas según el rol
    if rol == 'estudiante':
        usuario_obj = Usuario.obtener_por_id(usuario_id)
        if usuario_obj:
            contexto['mis_materias'] = len(usuario_obj.materias) if hasattr(usuario_obj, 'materias') else 0
            contexto['mis_tareas'] = 0  # Se calculará cuando tengamos el modelo de Entrega
    
    elif rol == 'profesor':
        tareas = Tarea.obtener_todas()
        contexto['mis_tareas'] = sum(1 for t in tareas if t.creado_por == usuario_id)
        grupos = Grupo.obtener_todos()
        contexto['mis_grupos'] = sum(1 for g in grupos if g.creado_por == usuario_id)
    
    elif rol == 'coordinador':
        contexto['usuarios_total'] = len(Usuario.obtener_todos())
        contexto['materias_total'] = len(Materia.obtener_todas())
        contexto['grupos_total'] = len(Grupo.obtener_todos())
    
    return render_template(
        'aplicacion/dashboard.html',
        page_title='Dashboard',
        active_page='dashboard',
        **contexto
    )