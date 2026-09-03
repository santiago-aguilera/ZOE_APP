"""
Rutas del blueprint de Parametrización.

Panel exclusivo del coordinador: activar/desactivar módulos completos del
sistema, restringir el acceso por rol y editar ajustes generales, todo sin
tocar código. Organizado como cards por tema.
"""

from flask import render_template, request, redirect, url_for, flash

from app.blueprints import parametrizacion_bp
from app.models import (ModuloSistema, RolPermiso, ConfiguracionSistema, ROLES_SISTEMA,
                        ACCIONES_POR_MODULO, ETIQUETAS_ACCION, MODULOS_CON_ACCIONES, MODULOS_POR_DEFECTO)
from app.decorators import roles_permitidos


@parametrizacion_bp.route('/')
@roles_permitidos('coordinador')
def inicio():
    """Landing del panel: una card por tema de parametrización."""
    modulos = ModuloSistema.obtener_todos()
    return render_template(
        'aplicacion/parametrizacion/inicio.html',
        page_title='Parametrización',
        active_page='parametrizacion',
        total_modulos=len(modulos),
        modulos_activos=sum(1 for m in modulos if m.activo)
    )


@parametrizacion_bp.route('/modulos')
@roles_permitidos('coordinador')
def modulos():
    """Card: activar/desactivar módulos completos del sistema."""
    return render_template(
        'aplicacion/parametrizacion/modulos.html',
        page_title='Módulos del sistema',
        active_page='parametrizacion',
        modulos=ModuloSistema.obtener_todos()
    )


@parametrizacion_bp.route('/modulos/<clave>/toggle', methods=['POST'])
@roles_permitidos('coordinador')
def toggle_modulo(clave):
    """Activa o desactiva un módulo (checkbox individual, guarda al toque)."""
    nuevo_estado = request.form.get('activo') == '1'
    ModuloSistema.actualizar_estado(clave, nuevo_estado)
    flash(f'Módulo {"activado" if nuevo_estado else "desactivado"}.', 'success')
    return redirect(url_for('parametrizacion.modulos'))


@parametrizacion_bp.route('/permisos')
@roles_permitidos('coordinador')
def permisos():
    """Card: matriz de qué rol puede VER cada módulo, y matriz granular de
    qué ACCIONES puede ejecutar cada rol dentro de los módulos con CRUD."""
    modulos = ModuloSistema.obtener_todos()
    matriz_ver = RolPermiso.obtener_matriz(accion='ver')
    matriz_completa = RolPermiso.obtener_matriz_completa()
    roles = [r for r in ROLES_SISTEMA if r != 'coordinador']  # el coordinador siempre ve todo

    nombres_modulo = {clave: nombre for clave, nombre, _ in MODULOS_POR_DEFECTO}
    nombres_modulo.update({'usuarios': 'Usuarios', 'matricula': 'Matrícula BI'})

    modulos_acciones = [
        {'clave': clave, 'nombre': nombres_modulo.get(clave, clave.capitalize()),
         'acciones': ACCIONES_POR_MODULO.get(clave, ('ver', 'crear', 'editar', 'eliminar'))}
        for clave in MODULOS_CON_ACCIONES
    ]

    return render_template(
        'aplicacion/parametrizacion/permisos.html',
        page_title='Roles y permisos',
        active_page='parametrizacion',
        modulos=modulos,
        matriz=matriz_ver,
        matriz_completa=matriz_completa,
        roles=roles,
        modulos_acciones=modulos_acciones,
        etiquetas_accion=ETIQUETAS_ACCION
    )


@parametrizacion_bp.route('/permisos/guardar', methods=['POST'])
@roles_permitidos('coordinador')
def guardar_permisos():
    """Guarda toda la matriz de permisos de una sola vez: visibilidad de
    módulo (checkboxes permiso_<rol>_<modulo>) Y acciones granulares
    (checkboxes accion_<rol>_<modulo>_<accion>)."""
    modulos = ModuloSistema.obtener_todos()
    roles = [r for r in ROLES_SISTEMA if r != 'coordinador']

    for rol in roles:
        for modulo in modulos:
            campo = f'permiso_{rol}_{modulo.clave}'
            permitido = campo in request.form
            RolPermiso.actualizar(rol, modulo.clave, permitido, accion='ver')

        for clave, acciones in ACCIONES_POR_MODULO.items():
            if clave not in MODULOS_CON_ACCIONES:
                continue
            for accion in acciones:
                if accion == 'ver':
                    continue
                campo = f'accion_{rol}_{clave}_{accion}'
                permitido = campo in request.form
                RolPermiso.actualizar(rol, clave, permitido, accion=accion)

    flash('Permisos actualizados.', 'success')
    return redirect(url_for('parametrizacion.permisos'))


@parametrizacion_bp.route('/general')
@roles_permitidos('coordinador')
def general():
    """Card: ajustes generales del sistema (clave/valor)."""
    return render_template(
        'aplicacion/parametrizacion/general.html',
        page_title='Configuración general',
        active_page='parametrizacion',
        ajustes=ConfiguracionSistema.obtener_todas()
    )


@parametrizacion_bp.route('/general/guardar', methods=['POST'])
@roles_permitidos('coordinador')
def guardar_general():
    """Guarda todos los ajustes generales de una sola vez."""
    for ajuste in ConfiguracionSistema.obtener_todas():
        clave = ajuste['clave']
        if ajuste['tipo'] == 'booleano':
            valor = '1' if request.form.get(f'ajuste_{clave}') == '1' else '0'
        else:
            valor = request.form.get(f'ajuste_{clave}', ajuste['valor'])
        ConfiguracionSistema.actualizar(clave, valor)
    flash('Configuración general actualizada.', 'success')
    return redirect(url_for('parametrizacion.general'))
