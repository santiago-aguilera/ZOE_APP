"""
Utilidad de solo lectura para mostrar, ANTES de eliminar un registro,
cuántas filas dependientes tiene. Es puramente informativa: la eliminación
en sí siempre se hace con un DELETE directo (ver Modelo.eliminar()), que
respeta las políticas CASCADE/SET NULL/RESTRICT definidas a nivel de base
de datos en DB.sql. Este archivo NO ejecuta eliminaciones — solo cuenta.
"""

from typing import List, Tuple
from app.config_db import db

# Mapa de qué contar antes de intentar eliminar cada entidad. Los valores
# reflejan la política real de la BD: si una fila aparece acá con un
# conteo > 0 y esa relación es RESTRICT, la eliminación va a fallar (y
# @eliminacion_segura la va a atrapar con un mensaje claro); si la
# relación es CASCADE, el conteo es solo informativo (se borraría junto
# con el padre).
DEPENDENCY_MAP = {
    'usuario': [
        ('entrega', 'SELECT COUNT(*) as cnt FROM entrega WHERE estudiante_id=%s'),
        ('estudiante_grupo', 'SELECT COUNT(*) as cnt FROM estudiante_grupo WHERE usuario_id=%s'),
        ('estudiante_especialidad', 'SELECT COUNT(*) as cnt FROM estudiante_especialidad WHERE usuario_id=%s'),
        ('recurso', 'SELECT COUNT(*) as cnt FROM recurso WHERE creado_por=%s'),
        ('cronograma', 'SELECT COUNT(*) as cnt FROM cronograma WHERE creado_por=%s'),
        ('comunicado', 'SELECT COUNT(*) as cnt FROM comunicado WHERE creado_por=%s'),
        ('tarea', 'SELECT COUNT(*) as cnt FROM tarea WHERE creado_por=%s'),
        ('grupo', 'SELECT COUNT(*) as cnt FROM grupo WHERE creado_por=%s'),
        ('actividad_valorativa', 'SELECT COUNT(*) as cnt FROM actividad_valorativa WHERE creado_por=%s'),
        ('proyecto_archivado', 'SELECT COUNT(*) as cnt FROM proyecto_archivado WHERE creado_por=%s'),
    ],
    'curso': [
        ('curso_materia', 'SELECT COUNT(*) as cnt FROM curso_materia WHERE curso_id=%s'),
        ('estudiante', "SELECT COUNT(*) as cnt FROM usuario WHERE curso_id=%s AND rol='estudiante'"),
        ('grupo', 'SELECT COUNT(*) as cnt FROM grupo WHERE curso_id=%s'),
    ],
    'materia': [
        ('curso_materia', 'SELECT COUNT(*) as cnt FROM curso_materia WHERE materia_id=%s'),
    ],
    'grupo': [
        ('estudiante_grupo', 'SELECT COUNT(*) as cnt FROM estudiante_grupo WHERE grupo_id=%s'),
    ],
    'tarea': [
        ('entrega', 'SELECT COUNT(*) as cnt FROM entrega WHERE tarea_id=%s'),
    ],
    'cohorte': [
        ('especialidad', 'SELECT COUNT(*) as cnt FROM especialidad WHERE cohorte_id=%s'),
        ('usuario', 'SELECT COUNT(*) as cnt FROM usuario WHERE cohorte_id=%s'),
    ],
}

# Columnas que necesitan el parámetro dos veces (WHERE x=%s OR y=%s)
_DOBLE_PARAMETRO = {
    ('usuario', 'mensaje'),
}


def listar_dependencias(entidad: str, entidad_id: int) -> List[Tuple[str, int]]:
    """Retorna [(tabla, cantidad), ...] con las filas dependientes que
    tiene un registro. Uso puramente informativo para avisar antes de
    eliminar; nunca elimina nada."""
    dependencias = []
    for tabla, count_sql in DEPENDENCY_MAP.get(entidad, []):
        try:
            if (entidad, tabla) in _DOBLE_PARAMETRO:
                resultados = db.ejecutar_consulta(count_sql, (entidad_id, entidad_id))
            else:
                resultados = db.ejecutar_consulta(count_sql, (entidad_id,))
            cnt = resultados[0]['cnt'] if resultados else 0
        except Exception:
            cnt = 0
        dependencias.append((tabla, cnt))
    return dependencias
