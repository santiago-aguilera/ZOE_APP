"""
Rutas del blueprint de Dashboard.
Pagina principal despues del login.
"""

from flask import render_template, session
from datetime import datetime

from app.blueprints import dashboard_bp
from app.models import Usuario, Tarea, Grupo, Materia, Mensaje, Entrega
from app.decorators import login_required


@dashboard_bp.route('/')
@login_required
def dashboard():
    """Dashboard principal con estadisticas reales segun el rol."""
    usuario_id = session.get('usuario_id')
    usuario = session.get('usuario', 'Usuario Demo')
    rol = session.get('rol', 'estudiante')

    # Fecha actual en espanol
    fecha = datetime.now().strftime("%A, %d de %B de %Y")
    traducciones = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miercoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sabado',
        'Sunday': 'Domingo', 'January': 'enero', 'February': 'febrero',
        'March': 'marzo', 'April': 'abril', 'May': 'mayo', 'June': 'junio',
        'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
        'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    for en, es in traducciones.items():
        fecha = fecha.replace(en, es)

    # Defaults en 0 para TODOS los roles, sin excepcion (nunca queda undefined).
    contexto = {
        'usuario': usuario,
        'usuario_id': usuario_id,
        'rol': rol,
        'fecha': fecha,
        'mis_materias': 0,
        'mis_tareas': 0,
        'entregas_completadas': 0,
        'mis_grupos': 0,
        'entregas_por_calificar': 0,
        'usuarios_total': 0,
        'materias_total': 0,
        'grupos_total': 0,
    }

    if rol == 'estudiante':
        contexto['mis_materias'] = len(Usuario.obtener_materias(usuario_id))
        contexto['mis_tareas'] = Usuario.contar_tareas_estudiante(usuario_id)
        contexto['entregas_completadas'] = Entrega.contar_completadas_estudiante(usuario_id)

    elif rol == 'profesor':
        tareas = Tarea.obtener_todas(profesor_id=usuario_id)
        contexto['mis_tareas'] = len(tareas)
        grupos = Grupo.obtener_todos()
        contexto['mis_grupos'] = sum(1 for g in grupos if g.creado_por == usuario_id)
        contexto['entregas_por_calificar'] = Entrega.contar_por_calificar_profesor(usuario_id)

    elif rol == 'coordinador':
        contexto['usuarios_total'] = len(Usuario.obtener_todos())
        contexto['materias_total'] = len(Materia.obtener_todas())
        contexto['grupos_total'] = len(Grupo.obtener_todos())

    # Progreso por materia (solo aplica al rol estudiante; lista vacia para los demas)
    contexto['progreso_materias'] = (
        Materia.progreso_estudiante(usuario_id) if rol == 'estudiante' else []
    )

    # Proximas entregas reales. Lista vacia = seccion "sin tareas proximas".
    if rol == 'estudiante':
        contexto['proximas_tareas'] = Tarea.obtener_para_estudiante(usuario_id)[:5]
    elif rol == 'profesor':
        contexto['proximas_tareas'] = Tarea.obtener_todas(profesor_id=usuario_id)[:5]
    else:
        contexto['proximas_tareas'] = Tarea.obtener_proximas(limite=5)

    # Mensajes no leidos, para la tarjeta y el badge del sidebar.
    contexto['mensajes_no_leidos'] = Mensaje.contar_no_leidos(usuario_id)

    # Tareas activas segun el rol, para el badge del sidebar (nunca todas
    # las del sistema para estudiante/profesor: solo las que le corresponden).
    if rol == 'estudiante':
        contexto['tareas_badge'] = len(Tarea.obtener_para_estudiante(usuario_id))
    elif rol == 'profesor':
        contexto['tareas_badge'] = len(Tarea.obtener_todas(profesor_id=usuario_id))
    else:
        contexto['tareas_badge'] = len(Tarea.obtener_todas())

    return render_template(
        'aplicacion/dashboard.html',
        page_title='Dashboard',
        active_page='dashboard',
        **contexto
    )