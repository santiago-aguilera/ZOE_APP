"""
Rutas del blueprint de Exportaciones.

Informes institucionales en Excel/CSV con filtros por cohorte, curso, materia,
estado de matrícula y periodo (año, semestre o rango de fechas).
Solo coordinador. Solo lectura: no modifica ninguna tabla.
"""

from datetime import datetime

from flask import (render_template, request, redirect, url_for, session, flash,
                   send_file, current_app)

from app.blueprints import exportaciones_bp
from app.models import (Cohorte, Curso, Materia, ConfiguracionSistema, ESTADOS_MATRICULA,
                        ETIQUETAS_ESTADO_MATRICULA)
from app.decorators import roles_permitidos, modulo_requerido
from app.blueprints.exportaciones import informes, escritor

MIME_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def _anios(cohortes):
    hoy = datetime.now().year
    años = {hoy}
    for c in cohortes:
        for fecha in (c.fecha_inicio, c.fecha_fin):
            if hasattr(fecha, 'year'):
                años.add(fecha.year)
    return sorted(años, reverse=True)


@exportaciones_bp.route('/')
@modulo_requerido('exportaciones')
@roles_permitidos('coordinador')
def inicio():
    cohortes = Cohorte.obtener_todos()
    nombres = {c.id: c.nombre for c in cohortes}
    cursos = [{'id': c.id, 'etiqueta': f"{c.codigo} · {nombres.get(c.cohorte_id, 'sin cohorte')}"}
              for c in Curso.obtener_todos()]
    return render_template(
        'aplicacion/exportaciones/exportaciones.html',
        page_title='Exportaciones',
        active_page='exportaciones',
        reportes=informes.REPORTES,
        cohortes=cohortes,
        cursos=cursos,
        materias=Materia.obtener_todas(),
        anios=_anios(cohortes),
        estados=[(e, ETIQUETAS_ESTADO_MATRICULA[e]) for e in ESTADOS_MATRICULA],
    )


@exportaciones_bp.route('/descargar')
@modulo_requerido('exportaciones')
@roles_permitidos('coordinador')
def descargar():
    clave = request.args.get('reporte', '')
    formato = request.args.get('formato', 'xlsx')
    if clave not in informes.REPORTES or formato not in ('xlsx', 'csv'):
        flash('Informe o formato no válido.', 'error')
        return redirect(url_for('exportaciones.inicio'))

    f = informes.filtros_desde_args(request.args)
    try:
        hojas, avisos = informes.construir(clave, f)
        base = f"zoe_{clave}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        if formato == 'csv':
            buf, nombre, mime = escritor.a_csv(hojas, base)
        else:
            portada = None
            if clave == 'completo':
                portada = {
                    'titulo': 'Informe institucional ZOE',
                    'institucion': ConfiguracionSistema.obtener('nombre_institucion', ''),
                    'filtros': informes.describir_filtros(f),
                    'generado_por': session.get('usuario', ''),
                }
            buf, nombre, mime = escritor.a_xlsx(hojas, portada), base + '.xlsx', MIME_XLSX
    except Exception:
        current_app.logger.exception('Error generando el informe %s', clave)
        flash('No se pudo generar el informe. Revisá que la base de datos tenga todas las tablas '
              '(descriptor, nota_prevista, informe_final) y probá de nuevo.', 'error')
        return redirect(url_for('exportaciones.inicio'))

    return send_file(buf, as_attachment=True, download_name=nombre, mimetype=mime)
