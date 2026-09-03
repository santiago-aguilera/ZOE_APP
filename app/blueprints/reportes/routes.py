"""
Rutas del blueprint de Reportes. Vista distinta por rol:
- coordinador: todo el sistema.
- profesor: solo sus materias.
- estudiante: su propio rendimiento.
"""

from flask import render_template, session

from app.blueprints import reportes_bp
from app.models import Entrega, Materia, Tarea, Usuario
from app.decorators import login_required


@reportes_bp.route('/')
@login_required
def reportes():
    rol = session.get('rol')
    usuario_id = session.get('usuario_id')

    if rol == 'estudiante':
        return _reportes_estudiante(usuario_id)

    materia_ids = Materia.obtener_ids_por_profesor(usuario_id) if rol == 'profesor' else None
    stats = Entrega.estadisticas_generales(materia_ids)
    detalle = Entrega.estadisticas_por_materia(materia_ids)

    # Distribución de desempeño (Bajo/Básico/Alto/Superior) a partir del promedio por materia
    distribucion = {'bajo': 0, 'basico': 0, 'alto': 0, 'superior': 0}
    for d in detalle:
        if d['promedio'] >= 18: distribucion['superior'] += 1
        elif d['promedio'] >= 14: distribucion['alto'] += 1
        elif d['promedio'] >= 10: distribucion['basico'] += 1
        else: distribucion['bajo'] += 1

    return render_template(
        'aplicacion/reportes/reportes.html',
        page_title='Reportes', active_page='reportes', rol=rol,
        promedio=stats['promedio'], tasa_calificadas=stats['tasa_calificadas'],
        tasa_a_tiempo=stats['tasa_a_tiempo'],
        progreso_materias=Materia.progreso_general(materia_ids),
        detalle_materias=detalle,
        top_estudiantes=Entrega.top_estudiantes(materia_ids, limite=5),
        tendencia_semanal=Entrega.entregas_por_semana(semanas=8),
        distribucion=distribucion,
        vista_limitada=(rol == 'profesor')
    )


def _reportes_estudiante(estudiante_id):
    """Vista personal: su propio avance, no la de sus compañeros."""
    progreso = Materia.progreso_estudiante(estudiante_id)
    total_tareas = len(Tarea.obtener_todas())
    completadas = Entrega.contar_completadas_estudiante(estudiante_id)
    pendientes = max(total_tareas - completadas, 0)
    promedio = round(sum(p['porcentaje'] for p in progreso) / len(progreso), 1) if progreso else 0

    return render_template(
        'aplicacion/reportes/reportes.html',
        page_title='Mi Rendimiento', active_page='reportes', rol='estudiante',
        progreso_materias=[{'nombre': p['materia'], 'porcentaje': p['porcentaje']} for p in progreso],
        entregas_completadas=completadas, entregas_pendientes=pendientes,
        avance_promedio=promedio
    )