"""
Constructores de informes institucionales de ZOE.

Cada informe es una función rep_xxx(f) que recibe el diccionario de filtros
y devuelve una lista de "hojas": {'nombre', 'cols', 'rows'}. Ninguna función
sabe nada de Excel ni CSV (eso vive en escritor.py), así que agregar un
informe nuevo es escribir una función y registrarla en REPORTES.

Solo hace SELECT: nunca modifica datos.
"""

from collections import OrderedDict
from datetime import datetime

from app.config_db import db
from app.models import (ESTADOS_MATRICULA, ETIQUETAS_ESTADO_MATRICULA,
                        ESCALA_VALORATIVA, VALOR_ORDINAL, ORDINAL_A_VALOR)

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _q(sql, params=()):
    """Ejecuta un SELECT verificando que los placeholders coincidan."""
    params = tuple(params)
    if sql.count('%s') != len(params):
        raise ValueError(f'Consulta mal armada: {sql.count("%s")} placeholders y {len(params)} parámetros')
    return db.ejecutar_consulta(sql, params)


def _donde(*pares):
    """Arma ' AND cond ...' solo con los filtros que tienen valor."""
    sql, params = '', []
    for frag, val in pares:
        if val in (None, ''):
            continue
        sql += ' AND ' + frag
        params.extend([val] * frag.count('%s'))
    return sql, params


def _hoja(nombre, cols, rows):
    return {'nombre': nombre, 'cols': cols, 'rows': rows}


def _estado(v):
    return ETIQUETAS_ESTADO_MATRICULA.get(v, v or 'No matriculado')


def _si_no(v):
    return 'Sí' if v else 'No'


def _pct(a, b):
    return round(a / b * 100, 1) if b else 0


def _fecha_valida(texto):
    try:
        return datetime.strptime((texto or '').strip(), '%Y-%m-%d').date().isoformat()
    except ValueError:
        return None


def filtros_desde_args(args):
    """Lee y valida los filtros de la URL. Nada llega a SQL sin validar."""
    def _int(k):
        return args.get(k, type=int) or None

    estado = args.get('estado') or None
    if estado not in ESTADOS_MATRICULA:
        estado = None

    desde = _fecha_valida(args.get('desde'))
    hasta = _fecha_valida(args.get('hasta'))
    anio = args.get('anio', type=int)
    semestre = args.get('semestre') or ''
    if not (desde or hasta) and anio:
        if semestre == '1':
            desde, hasta = f'{anio}-01-01', f'{anio}-06-30'
        elif semestre == '2':
            desde, hasta = f'{anio}-07-01', f'{anio}-12-31'
        else:
            desde, hasta = f'{anio}-01-01', f'{anio}-12-31'

    return {
        'cohorte_id': _int('cohorte_id'), 'curso_id': _int('curso_id'),
        'materia_id': _int('materia_id'), 'estado': estado,
        'desde': desde, 'hasta': hasta,
    }


def describir_filtros(f):
    """Texto legible de los filtros aplicados (para la portada)."""
    lineas = []
    if f['cohorte_id']:
        r = _q('SELECT nombre FROM cohorte WHERE id=%s', (f['cohorte_id'],))
        lineas.append('Cohorte: ' + (r[0]['nombre'] if r else str(f['cohorte_id'])))
    if f['curso_id']:
        r = _q('SELECT codigo FROM curso WHERE id=%s', (f['curso_id'],))
        lineas.append('Curso: ' + (str(r[0]['codigo']) if r else str(f['curso_id'])))
    if f['materia_id']:
        r = _q('SELECT nombre FROM materia WHERE id=%s', (f['materia_id'],))
        lineas.append('Materia: ' + (r[0]['nombre'] if r else str(f['materia_id'])))
    if f['estado']:
        lineas.append('Estado de matrícula: ' + _estado(f['estado']))
    if f['desde'] or f['hasta']:
        lineas.append(f"Periodo: {f['desde'] or 'inicio'} a {f['hasta'] or 'hoy'}")
    return lineas or ['Sin filtros (toda la información)']


# ---------------------------------------------------------------------------
# Informes
# ---------------------------------------------------------------------------

def rep_estudiantes(f):
    w, p = _donde(('u.cohorte_id = %s', f['cohorte_id']),
                  ('u.curso_id = %s', f['curso_id']),
                  ('u.estado_matricula = %s', f['estado']))
    filas = _q(f"""
        SELECT u.id, u.nombre, u.correo, co.nombre AS cohorte, c.codigo AS curso,
               c.grado, u.estado_matricula, u.activo
        FROM usuario u
        LEFT JOIN cohorte co ON co.id = u.cohorte_id
        LEFT JOIN curso c ON c.id = u.curso_id
        WHERE u.rol = 'estudiante'{w}
        ORDER BY co.nombre, c.codigo, u.nombre""", p)
    rows = [[r['id'], r['nombre'], r['correo'], r['cohorte'] or 'Sin cohorte',
             r['curso'] or 'Sin curso', f"{r['grado']}°" if r['grado'] else '',
             _estado(r['estado_matricula']), _si_no(r['activo'])] for r in filas]
    return [_hoja('Estudiantes', ['ID', 'Nombre', 'Correo', 'Cohorte', 'Curso', 'Grado',
                                  'Matrícula BI', 'Activo'], rows)]


def rep_matricula_bi(f):
    w, p = _donde(('u.cohorte_id = %s', f['cohorte_id']), ('u.curso_id = %s', f['curso_id']))
    filas = _q(f"""
        SELECT co.nombre AS cohorte, c.codigo AS curso,
               COALESCE(u.estado_matricula, 'NO_MATRICULADO') AS estado, COUNT(*) AS total
        FROM usuario u
        LEFT JOIN cohorte co ON co.id = u.cohorte_id
        LEFT JOIN curso c ON c.id = u.curso_id
        WHERE u.rol = 'estudiante'{w}
        GROUP BY co.nombre, c.codigo, COALESCE(u.estado_matricula, 'NO_MATRICULADO')
        ORDER BY co.nombre, c.codigo""", p)

    def pivot(clave):
        acum = OrderedDict()
        for r in filas:
            k = clave(r)
            fila = acum.setdefault(k, {e: 0 for e in ESTADOS_MATRICULA})
            fila[r['estado']] = fila.get(r['estado'], 0) + r['total']
        return [list(k) + [v[e] for e in ESTADOS_MATRICULA] + [sum(v.values())]
                for k, v in acum.items()]

    etiquetas = [ETIQUETAS_ESTADO_MATRICULA[e] for e in ESTADOS_MATRICULA]
    return [
        _hoja('Matrícula BI por cohorte', ['Cohorte'] + etiquetas + ['Total'],
              pivot(lambda r: (r['cohorte'] or 'Sin cohorte',))),
        _hoja('Matrícula BI por curso', ['Cohorte', 'Curso'] + etiquetas + ['Total'],
              pivot(lambda r: (r['cohorte'] or 'Sin cohorte', r['curso'] or 'Sin curso'))),
    ]


def rep_valoraciones(f):
    # Las actividades sin fecha se incluyen siempre; las fechadas, solo dentro del periodo.
    jd, jp = '', []
    if f['desde']:
        jd += ' AND (ae.fecha IS NULL OR ae.fecha >= %s)'
        jp.append(f['desde'])
    if f['hasta']:
        jd += ' AND (ae.fecha IS NULL OR ae.fecha <= %s)'
        jp.append(f['hasta'])
    w, wp = _donde(('u.cohorte_id = %s', f['cohorte_id']), ('u.curso_id = %s', f['curso_id']),
                   ('m.id = %s', f['materia_id']))
    filas = _q(f"""
        SELECT u.id AS est_id, u.nombre AS estudiante, co.nombre AS cohorte, c.codigo AS curso,
               m.id AS materia_id, m.nombre AS materia, m.tipo AS materia_tipo,
               m.valoracion_minima_aprobatoria AS umbral,
               ae.id AS act_id, ae.nombre AS actividad, ae.tipo AS act_tipo,
               ae.porcentaje, ae.fecha, va.valor, va.comentario
        FROM usuario u
        JOIN curso c ON c.id = u.curso_id
        JOIN curso_materia cm ON cm.curso_id = u.curso_id
        JOIN materia m ON m.id = cm.materia_id
        LEFT JOIN cohorte co ON co.id = u.cohorte_id
        LEFT JOIN actividad_valorativa ae ON ae.materia_id = m.id{jd}
        LEFT JOIN valoracion_actividad va ON va.actividad_id = ae.id AND va.estudiante_id = u.id
        WHERE u.rol = 'estudiante'{w}
        ORDER BY co.nombre, c.codigo, u.nombre, m.nombre, ae.fecha, ae.id""", jp + wp)

    grupos, detalle = OrderedDict(), []
    for r in filas:
        g = grupos.setdefault((r['est_id'], r['materia_id']), {
            'r': r, 'acts': set(), 'cal': set(), 'suma': 0.0, 'peso': 0.0})
        if r['act_id'] is None:
            continue
        g['acts'].add(r['act_id'])
        detalle.append([r['cohorte'] or '', r['curso'], r['estudiante'], r['materia'],
                        r['actividad'], (r['act_tipo'] or '').capitalize(),
                        float(r['porcentaje'] or 0), r['fecha'] or '',
                        r['valor'] or 'Sin valorar', r['comentario'] or ''])
        if r['valor']:
            peso = float(r['porcentaje'] or 0)
            g['cal'].add(r['act_id'])
            g['suma'] += VALOR_ORDINAL[r['valor']] * peso
            g['peso'] += peso

    boletin, dist = [], OrderedDict()
    for g in grupos.values():
        r = g['r']
        if g['peso'] > 0:
            final = ORDINAL_A_VALOR[min(4, max(1, round(g['suma'] / g['peso'])))]
        else:
            final = None
        completo = bool(g['acts']) and len(g['acts']) == len(g['cal'])
        aprobado = final is not None and VALOR_ORDINAL[final] >= VALOR_ORDINAL.get(r['umbral'], 2)
        if final is None:
            estado = 'Sin valorar'
        elif aprobado:
            estado = 'Aprobado' if completo else 'Aprobado (provisional)'
        else:
            estado = 'Reprobado' if completo else 'En riesgo (provisional)'
        boletin.append([r['cohorte'] or '', r['curso'], r['estudiante'], r['materia'],
                        r['materia_tipo'], f"{len(g['cal'])}/{len(g['acts'])}",
                        final or '—', r['umbral'], estado])
        d = dist.setdefault((r['cohorte'] or '', r['curso'], r['materia']),
                            {'n': 0, 'sin': 0, 'apr': 0, **{v: 0 for v in ESCALA_VALORATIVA}})
        d['n'] += 1
        if final is None:
            d['sin'] += 1
        else:
            d[final] += 1
            d['apr'] += 1 if aprobado else 0

    resumen = [[k[0], k[1], k[2], d['n']] + [d[v] for v in ESCALA_VALORATIVA]
               + [d['sin'], _pct(d['apr'], d['n'] - d['sin'])] for k, d in dist.items()]
    return [
        _hoja('Boletín valoraciones',
              ['Cohorte', 'Curso', 'Estudiante', 'Materia', 'Tipo materia', 'Actividades valoradas',
               'Valoración final', 'Mínimo aprobatorio', 'Estado'], boletin),
        _hoja('Resumen por materia',
              ['Cohorte', 'Curso', 'Materia', 'Estudiantes'] + list(ESCALA_VALORATIVA)
              + ['Sin valorar', '% aprobación (de valorados)'], resumen),
        _hoja('Detalle por actividad',
              ['Cohorte', 'Curso', 'Estudiante', 'Materia', 'Actividad', 'Tipo', '% peso',
               'Fecha', 'Valoración', 'Comentario'], detalle),
    ]


def rep_tareas(f):
    w, p = _donde(('c.cohorte_id = %s', f['cohorte_id']), ('cm.curso_id = %s', f['curso_id']),
                  ('cm.materia_id = %s', f['materia_id']),
                  ('t.fecha_limite >= %s', f['desde']), ('t.fecha_limite <= %s', f['hasta']))
    resumen = _q(f"""
        SELECT t.id, t.titulo, t.fecha_limite, m.nombre AS materia, c.codigo AS curso,
               co.nombre AS cohorte, up.nombre AS profesor,
               (SELECT COUNT(*) FROM usuario x WHERE x.curso_id = cm.curso_id AND x.rol = 'estudiante') AS destinatarios,
               COUNT(e.id) AS entregas,
               COALESCE(SUM(e.estado = 'calificada'), 0) AS calificadas,
               COALESCE(SUM(DATE(e.fecha_entrega) <= t.fecha_limite), 0) AS a_tiempo,
               AVG(CASE WHEN e.calificacion REGEXP '^[0-9]+([.][0-9]+)?$'
                        THEN CAST(e.calificacion AS DECIMAL(6,2)) END) AS promedio
        FROM tarea t
        JOIN curso_materia cm ON cm.id = t.curso_materia_id
        JOIN materia m ON m.id = cm.materia_id
        JOIN curso c ON c.id = cm.curso_id
        LEFT JOIN cohorte co ON co.id = c.cohorte_id
        LEFT JOIN usuario up ON up.id = cm.profesor_id
        LEFT JOIN entrega e ON e.tarea_id = t.id
        WHERE 1 = 1{w}
        GROUP BY t.id, t.titulo, t.fecha_limite, m.nombre, c.codigo, co.nombre, up.nombre, cm.curso_id
        ORDER BY co.nombre, c.codigo, t.fecha_limite""", p)
    filas_res = [[r['cohorte'] or '', r['curso'], r['materia'], r['profesor'] or 'Sin asignar',
                  r['titulo'], r['fecha_limite'], r['destinatarios'], r['entregas'],
                  _pct(r['entregas'], r['destinatarios']), int(r['calificadas']),
                  _pct(int(r['a_tiempo']), r['entregas']),
                  round(float(r['promedio']), 1) if r['promedio'] is not None else '']
                 for r in resumen]

    det = _q(f"""
        SELECT co.nombre AS cohorte, c.codigo AS curso, m.nombre AS materia, t.titulo,
               t.fecha_limite, ue.nombre AS estudiante, e.estado, e.calificacion,
               e.fecha_entrega, e.comentario_profesor
        FROM tarea t
        JOIN curso_materia cm ON cm.id = t.curso_materia_id
        JOIN materia m ON m.id = cm.materia_id
        JOIN curso c ON c.id = cm.curso_id
        JOIN usuario ue ON ue.curso_id = cm.curso_id AND ue.rol = 'estudiante'
        LEFT JOIN cohorte co ON co.id = c.cohorte_id
        LEFT JOIN entrega e ON e.tarea_id = t.id AND e.estudiante_id = ue.id
        WHERE 1 = 1{w}
        ORDER BY co.nombre, c.codigo, t.fecha_limite, t.id, ue.nombre""", p)
    filas_det = []
    for r in det:
        entregada = r['fecha_entrega'] is not None
        a_tiempo = ''
        if entregada:
            a_tiempo = _si_no(r['fecha_entrega'].date() <= r['fecha_limite']) \
                if hasattr(r['fecha_entrega'], 'date') else ''
        filas_det.append([r['cohorte'] or '', r['curso'], r['materia'], r['titulo'],
                          r['fecha_limite'], r['estudiante'], r['estado'] or 'Sin entregar',
                          r['calificacion'] or '', r['fecha_entrega'] or '', a_tiempo,
                          r['comentario_profesor'] or ''])
    return [
        _hoja('Tareas resumen',
              ['Cohorte', 'Curso', 'Materia', 'Profesor', 'Tarea', 'Fecha límite', 'Estudiantes',
               'Entregas', '% entrega', 'Calificadas', '% a tiempo', 'Promedio nota'], filas_res),
        _hoja('Entregas detalle',
              ['Cohorte', 'Curso', 'Materia', 'Tarea', 'Fecha límite', 'Estudiante', 'Estado',
               'Calificación', 'Fecha entrega', 'A tiempo', 'Comentario profesor'], filas_det),
    ]


def rep_nota_prevista(f):
    w, p = _donde(('u.cohorte_id = %s', f['cohorte_id']), ('u.curso_id = %s', f['curso_id']),
                  ('np.materia_id = %s', f['materia_id']),
                  ('DATE(np.fecha_registro) >= %s', f['desde']),
                  ('DATE(np.fecha_registro) <= %s', f['hasta']))
    filas = _q(f"""
        SELECT co.nombre AS cohorte, c.codigo AS curso, u.id AS est_id, u.nombre AS estudiante,
               m.nombre AS materia, np.valor, up.nombre AS profesor, np.fecha_registro
        FROM nota_prevista np
        JOIN usuario u ON u.id = np.usuario_id
        JOIN materia m ON m.id = np.materia_id
        LEFT JOIN usuario up ON up.id = np.profesor_id
        LEFT JOIN curso c ON c.id = u.curso_id
        LEFT JOIN cohorte co ON co.id = u.cohorte_id
        WHERE 1 = 1{w}
        ORDER BY co.nombre, c.codigo, u.nombre, m.nombre""", p)
    detalle = [[r['cohorte'] or '', r['curso'] or '', r['estudiante'], r['materia'],
                float(r['valor']), r['profesor'] or '', r['fecha_registro']] for r in filas]
    prom = OrderedDict()
    for r in filas:
        d = prom.setdefault(r['est_id'], {'r': r, 'v': []})
        d['v'].append(float(r['valor']))
    promedios = [[d['r']['cohorte'] or '', d['r']['curso'] or '', d['r']['estudiante'],
                  len(d['v']), round(sum(d['v']) / len(d['v']), 2)] for d in prom.values()]
    return [
        _hoja('Nota prevista detalle',
              ['Cohorte', 'Curso', 'Estudiante', 'Materia', 'Nota prevista (1-7)', 'Profesor',
               'Fecha registro'], detalle),
        _hoja('Nota prevista promedio',
              ['Cohorte', 'Curso', 'Estudiante', 'Materias con nota', 'Promedio (1-7)'], promedios),
    ]


def rep_informe_final(f):
    w, p = _donde(('inf.cohorte_id = %s', f['cohorte_id']), ('u.curso_id = %s', f['curso_id']),
                  ('m.id = %s', f['materia_id']))
    filas = _q(f"""
        SELECT co.nombre AS cohorte, c.codigo AS curso, u.id AS est_id, u.nombre AS estudiante,
               m.nombre AS materia, m.tipo AS materia_tipo, d.texto AS descriptor,
               ifd.alcanzo_prellenado, ifd.alcanzo, ifd.recomendacion
        FROM informe_final inf
        JOIN usuario u ON u.id = inf.usuario_id
        JOIN informe_final_detalle ifd ON ifd.informe_final_id = inf.id
        JOIN descriptor d ON d.id = ifd.descriptor_id
        JOIN materia m ON m.id = d.materia_id
        LEFT JOIN curso c ON c.id = u.curso_id
        LEFT JOIN cohorte co ON co.id = inf.cohorte_id
        WHERE 1 = 1{w}
        ORDER BY co.nombre, c.codigo, u.nombre, m.tipo, m.nombre""", p)

    def marca(v):
        return '' if v is None else _si_no(v)
    detalle = [[r['cohorte'] or '', r['curso'] or '', r['estudiante'], r['materia'],
                r['materia_tipo'], r['descriptor'], marca(r['alcanzo_prellenado']),
                marca(r['alcanzo']), r['recomendacion'] or ''] for r in filas]
    res = OrderedDict()
    for r in filas:
        d = res.setdefault(r['est_id'], {'r': r, 'n': 0, 'ok': 0, 'rec': 0})
        d['n'] += 1
        d['ok'] += 1 if r['alcanzo'] else 0
        d['rec'] += 1 if r['recomendacion'] else 0
    resumen = [[d['r']['cohorte'] or '', d['r']['curso'] or '', d['r']['estudiante'],
                d['n'], d['ok'], _pct(d['ok'], d['n']), d['rec']] for d in res.values()]
    return [
        _hoja('Informe final resumen',
              ['Cohorte', 'Curso', 'Estudiante', 'Componentes', 'Alcanzó', '% alcanzado',
               'Con recomendación'], resumen),
        _hoja('Informe final detalle',
              ['Cohorte', 'Curso', 'Estudiante', 'Materia', 'Tipo', 'Descriptor',
               'Alcanzó (sugerido)', 'Alcanzó (final)', 'Recomendación'], detalle),
    ]


def rep_asignaciones(f):
    w, p = _donde(('c.cohorte_id = %s', f['cohorte_id']), ('cm.curso_id = %s', f['curso_id']),
                  ('cm.materia_id = %s', f['materia_id']))
    filas = _q(f"""
        SELECT co.nombre AS cohorte, c.codigo AS curso, c.grado, m.nombre AS materia,
               m.tipo AS materia_tipo, up.nombre AS profesor,
               (SELECT COUNT(*) FROM usuario x WHERE x.curso_id = c.id AND x.rol = 'estudiante') AS estudiantes,
               (SELECT COUNT(*) FROM tarea t WHERE t.curso_materia_id = cm.id) AS tareas
        FROM curso_materia cm
        JOIN curso c ON c.id = cm.curso_id
        JOIN materia m ON m.id = cm.materia_id
        LEFT JOIN cohorte co ON co.id = c.cohorte_id
        LEFT JOIN usuario up ON up.id = cm.profesor_id
        WHERE 1 = 1{w}
        ORDER BY co.nombre, c.grado, c.codigo, m.nombre""", p)
    rows = [[r['cohorte'] or '', r['curso'], f"{r['grado']}°", r['materia'], r['materia_tipo'],
             r['profesor'] or 'Sin asignar', r['estudiantes'], r['tareas']] for r in filas]
    return [_hoja('Asignaciones académicas',
                  ['Cohorte', 'Curso', 'Grado', 'Materia', 'Tipo', 'Profesor', 'Estudiantes',
                   'Tareas'], rows)]


def rep_especialidades(f):
    w, p = _donde(('e.cohorte_id = %s', f['cohorte_id']))
    resumen = _q(f"""
        SELECT co.nombre AS cohorte, e.nombre AS especialidad, up.nombre AS profesor,
               COUNT(DISTINCT ee.usuario_id) AS estudiantes
        FROM especialidad e
        LEFT JOIN cohorte co ON co.id = e.cohorte_id
        LEFT JOIN usuario up ON up.id = e.profesor_id
        LEFT JOIN estudiante_especialidad ee ON ee.especialidad_id = e.id
        WHERE 1 = 1{w}
        GROUP BY e.id, co.nombre, e.nombre, up.nombre
        ORDER BY co.nombre, e.nombre""", p)
    det = _q(f"""
        SELECT co.nombre AS cohorte, e.nombre AS especialidad, u.nombre AS estudiante,
               u.correo, c.codigo AS curso
        FROM estudiante_especialidad ee
        JOIN especialidad e ON e.id = ee.especialidad_id
        JOIN usuario u ON u.id = ee.usuario_id
        LEFT JOIN cohorte co ON co.id = e.cohorte_id
        LEFT JOIN curso c ON c.id = u.curso_id
        WHERE 1 = 1{w}
        ORDER BY co.nombre, e.nombre, u.nombre""", p)
    return [
        _hoja('Especialidades',
              ['Cohorte', 'Especialidad', 'Profesor', 'Estudiantes'],
              [[r['cohorte'] or '', r['especialidad'], r['profesor'] or 'Sin asignar',
                r['estudiantes']] for r in resumen]),
        _hoja('Estudiantes por especialidad',
              ['Cohorte', 'Especialidad', 'Estudiante', 'Correo', 'Curso'],
              [[r['cohorte'] or '', r['especialidad'], r['estudiante'], r['correo'],
                r['curso'] or ''] for r in det]),
    ]


def rep_grupos(f):
    w, p = _donde(('g.cohorte_id = %s', f['cohorte_id']), ('g.curso_id = %s', f['curso_id']),
                  ('g.materia_id = %s', f['materia_id']))
    filas = _q(f"""
        SELECT g.nombre, m.nombre AS materia, c.codigo AS curso, co.nombre AS cohorte,
               uc.nombre AS creador, g.activo, COUNT(DISTINCT eg.usuario_id) AS estudiantes
        FROM grupo g
        LEFT JOIN materia m ON m.id = g.materia_id
        LEFT JOIN curso c ON c.id = g.curso_id
        LEFT JOIN cohorte co ON co.id = g.cohorte_id
        LEFT JOIN usuario uc ON uc.id = g.creado_por
        LEFT JOIN estudiante_grupo eg ON eg.grupo_id = g.id
        WHERE 1 = 1{w}
        GROUP BY g.id, g.nombre, m.nombre, c.codigo, co.nombre, uc.nombre, g.activo
        ORDER BY g.nombre""", p)
    return [_hoja('Grupos de estudio',
                  ['Grupo', 'Materia', 'Curso', 'Cohorte', 'Creado por', 'Activo', 'Estudiantes'],
                  [[r['nombre'], r['materia'] or '', r['curso'] or '', r['cohorte'] or '',
                    r['creador'] or '', _si_no(r['activo']), r['estudiantes']] for r in filas])]


def rep_cronograma(f):
    w, p = _donde(('(c.cohorte_id = %s OR cr.curso_id IS NULL)', f['cohorte_id']),
                  ('cr.curso_id = %s', f['curso_id']), ('cr.materia_id = %s', f['materia_id']),
                  ('cr.fecha_evento >= %s', f['desde']), ('cr.fecha_evento <= %s', f['hasta']))
    filas = _q(f"""
        SELECT cr.fecha_evento, cr.titulo, cr.tipo, m.nombre AS materia, c.codigo AS curso,
               cr.descripcion
        FROM cronograma cr
        LEFT JOIN materia m ON m.id = cr.materia_id
        LEFT JOIN curso c ON c.id = cr.curso_id
        WHERE 1 = 1{w}
        ORDER BY cr.fecha_evento""", p)
    return [_hoja('Cronograma',
                  ['Fecha', 'Evento', 'Tipo', 'Materia', 'Curso', 'Descripción'],
                  [[r['fecha_evento'], r['titulo'], (r['tipo'] or '').capitalize(),
                    r['materia'] or 'Institucional', r['curso'] or 'Todos',
                    r['descripcion'] or ''] for r in filas])]


def rep_archivo(f):
    w, p = _donde(('p.cohorte_id = %s', f['cohorte_id']), ('p.materia_id = %s', f['materia_id']),
                  ('DATE(p.creado_en) >= %s', f['desde']), ('DATE(p.creado_en) <= %s', f['hasta']))
    filas = _q(f"""
        SELECT p.titulo, p.autor, m.nombre AS materia, co.nombre AS cohorte,
               p.palabras_clave, p.url_archivo, p.creado_en
        FROM proyecto_archivado p
        LEFT JOIN materia m ON m.id = p.materia_id
        LEFT JOIN cohorte co ON co.id = p.cohorte_id
        WHERE 1 = 1{w}
        ORDER BY co.nombre, p.titulo""", p)
    return [_hoja('Archivo histórico',
                  ['Título', 'Autor(es)', 'Materia', 'Cohorte', 'Palabras clave', 'Enlace',
                   'Archivado el'],
                  [[r['titulo'], r['autor'] or '', r['materia'] or '', r['cohorte'] or '',
                    r['palabras_clave'] or '', r['url_archivo'] or '', r['creado_en']]
                   for r in filas])]


def rep_resumen(f):
    dj, dp = _donde(('t.fecha_limite >= %s', f['desde']), ('t.fecha_limite <= %s', f['hasta']))
    wc, wp = _donde(('co.id = %s', f['cohorte_id']))
    filas = _q(f"""
        SELECT co.nombre, co.fecha_inicio, co.fecha_fin, co.activo,
          (SELECT COUNT(*) FROM usuario u WHERE u.cohorte_id = co.id AND u.rol = 'estudiante') AS estudiantes,
          (SELECT COUNT(*) FROM usuario u WHERE u.cohorte_id = co.id AND u.rol = 'estudiante'
             AND u.estado_matricula IN ('MATRICULADO', 'ACTIVO')) AS matriculados,
          (SELECT COUNT(*) FROM curso c WHERE c.cohorte_id = co.id AND c.grado = 10) AS decimos,
          (SELECT COUNT(*) FROM curso c WHERE c.cohorte_id = co.id AND c.grado = 11) AS onces,
          (SELECT COUNT(*) FROM especialidad e WHERE e.cohorte_id = co.id) AS especialidades,
          (SELECT COUNT(*) FROM tarea t JOIN curso_materia cm ON cm.id = t.curso_materia_id
             JOIN curso c ON c.id = cm.curso_id WHERE c.cohorte_id = co.id{dj}) AS tareas,
          (SELECT COUNT(*) FROM entrega e JOIN tarea t ON t.id = e.tarea_id
             JOIN curso_materia cm ON cm.id = t.curso_materia_id
             JOIN curso c ON c.id = cm.curso_id WHERE c.cohorte_id = co.id{dj}) AS entregas
        FROM cohorte co
        WHERE 1 = 1{wc}
        ORDER BY co.fecha_inicio""", dp + dp + wp)
    rows = [[r['nombre'], r['fecha_inicio'], r['fecha_fin'], _si_no(r['activo']),
             r['estudiantes'], r['matriculados'], _pct(r['matriculados'], r['estudiantes']),
             r['decimos'], r['onces'], r['especialidades'], r['tareas'], r['entregas']]
            for r in filas]
    return [_hoja('Resumen por cohorte',
                  ['Cohorte', 'Inicio', 'Fin', 'Activa', 'Estudiantes', 'Matriculados BI',
                   '% matriculados', 'Cursos décimo', 'Cursos once', 'Especialidades',
                   'Tareas', 'Entregas'], rows)] + rep_matricula_bi(f)


# ---------------------------------------------------------------------------
# Registro de informes (lo que ve la pantalla)
# ---------------------------------------------------------------------------

REPORTES = OrderedDict([
    ('completo', {'titulo': 'Informe institucional completo',
                  'descripcion': 'Todos los informes en un solo libro de Excel, con portada y filtros aplicados.',
                  'filtros': ('cohorte', 'curso', 'materia', 'periodo', 'estado'), 'fn': None}),
    ('resumen', {'titulo': 'Resumen por cohorte y matrícula BI',
                 'descripcion': 'Estudiantes, matriculados, cursos, especialidades, tareas y entregas por cohorte, más matrícula BI por estado.',
                 'filtros': ('cohorte', 'curso', 'periodo'), 'fn': rep_resumen}),
    ('estudiantes', {'titulo': 'Listado de estudiantes',
                     'descripcion': 'Cohorte, curso, grado y estado de matrícula BI de cada estudiante.',
                     'filtros': ('cohorte', 'curso', 'estado'), 'fn': rep_estudiantes}),
    ('valoraciones', {'titulo': 'Valoraciones (Bajo/Básico/Alto/Superior)',
                      'descripcion': 'Boletín por estudiante y materia, resumen por materia y detalle por actividad.',
                      'filtros': ('cohorte', 'curso', 'materia', 'periodo'), 'fn': rep_valoraciones}),
    ('tareas', {'titulo': 'Tareas y entregas',
                'descripcion': 'Cumplimiento por tarea (entregas, a tiempo, promedio) y detalle por estudiante, incluidos los que no entregaron.',
                'filtros': ('cohorte', 'curso', 'materia', 'periodo'), 'fn': rep_tareas}),
    ('nota_prevista', {'titulo': 'Nota prevista',
                       'descripcion': 'Nota prevista (1-7) por estudiante y materia normal, con promedio.',
                       'filtros': ('cohorte', 'curso', 'materia', 'periodo'), 'fn': rep_nota_prevista}),
    ('informe_final', {'titulo': 'Informe final por descriptor',
                       'descripcion': 'Alcanzó (sugerido y final) y recomendación por componente y estudiante.',
                       'filtros': ('cohorte', 'curso', 'materia'), 'fn': rep_informe_final}),
    ('asignaciones', {'titulo': 'Asignaciones académicas',
                      'descripcion': 'Curso, materia, profesor, estudiantes y tareas de cada asignación.',
                      'filtros': ('cohorte', 'curso', 'materia'), 'fn': rep_asignaciones}),
    ('especialidades', {'titulo': 'Especialidades',
                        'descripcion': 'Profesor y estudiantes de cada especialidad por cohorte.',
                        'filtros': ('cohorte',), 'fn': rep_especialidades}),
    ('grupos', {'titulo': 'Grupos de estudio',
                'descripcion': 'Grupos con su contexto y cantidad de integrantes.',
                'filtros': ('cohorte', 'curso', 'materia'), 'fn': rep_grupos}),
    ('cronograma', {'titulo': 'Cronograma',
                    'descripcion': 'Eventos institucionales y académicos del periodo.',
                    'filtros': ('cohorte', 'curso', 'materia', 'periodo'), 'fn': rep_cronograma}),
    ('archivo', {'titulo': 'Archivo histórico',
                 'descripcion': 'Proyectos archivados con autor, materia y cohorte.',
                 'filtros': ('cohorte', 'materia', 'periodo'), 'fn': rep_archivo}),
])


def construir(clave, f):
    """Devuelve (hojas, avisos). En 'completo', un informe con error no tumba el resto."""
    if clave != 'completo':
        return REPORTES[clave]['fn'](f), []
    hojas, avisos = [], []
    for k, meta in REPORTES.items():
        if k == 'completo':
            continue
        try:
            hojas.extend(meta['fn'](f))
        except Exception as e:  # tabla faltante, migración pendiente, etc.
            avisos.append(f"{meta['titulo']}: {e}")
    if avisos:
        hojas.append(_hoja('Avisos', ['Informe que no se pudo generar'], [[a] for a in avisos]))
    return hojas, avisos
