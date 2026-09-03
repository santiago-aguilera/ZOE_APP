"""
ZOE - Plataforma de Gestión Documental para el IB
Application Factory Pattern
"""

import os
from flask import Flask, session, url_for
from datetime import datetime

from app.config_db import config, db
from app.blueprints import (
    auth_bp, dashboard_bp, tareas_bp, materias_bp, grupos_bp, cursos_bp, especialidades_bp,
    comunicados_bp, recursos_bp, cronograma_bp, mensajeria_bp,
    reportes_bp, configuracion_bp, usuarios_bp, valoraciones_bp, archivo_bp, parametrizacion_bp, matricula_bp
)

# Carpeta donde se guardan los archivos de las entregas de tareas
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'app', 'static', 'uploads', 'entregas')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
                       'png', 'jpg', 'jpeg', 'zip', 'txt'}
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB máximo por archivo


def create_app(config_name="development"):
    """
    Factory function para crear la aplicación Flask.
    
    Args:
        config_name: Nombre de la configuración ('development', 'production', 'default')
    
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])

    # Configuración de subida de archivos (entregas de tareas)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # Variables globales para templates Jinja2
    @app.context_processor
    def variables_globales():
        from app.models import ModuloSistema, RolPermiso

        rol_actual = session.get("rol", "invitado")
        modulos_activos = {}
        permisos_rol = {}
        if session.get("usuario_id"):
            try:
                modulos_activos = ModuloSistema.mapa_activos()
                permisos_rol = {clave: RolPermiso.tiene_permiso(rol_actual, clave) for clave in modulos_activos}
            except Exception:
                # Si la BD no tiene todavía las tablas de Parametrización
                # (ej: no se re-importó DB.sql), no rompemos el sidebar.
                modulos_activos = {}
                permisos_rol = {}

        def modulo_visible(clave):
            """True si el módulo está activo Y el rol actual tiene permiso.
            Fail-open: si no hay datos (tabla vacía o BD vieja), se muestra."""
            return modulos_activos.get(clave, True) and permisos_rol.get(clave, True)

        return {
            "app_name": "ZOE IB",
            "usuario_id": session.get("usuario_id"),
            "usuario": session.get("usuario", "Usuario Demo"),
            "correo": session.get("correo", ""),
            "rol": rol_actual,
            "modulo_visible": modulo_visible,
        }
    
    # Registrar blueprints con sus prefijos de URL
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(tareas_bp, url_prefix='/tareas')
    app.register_blueprint(materias_bp, url_prefix='/materias')
    app.register_blueprint(grupos_bp, url_prefix='/grupos')
    app.register_blueprint(cursos_bp, url_prefix='/cursos')
    app.register_blueprint(especialidades_bp, url_prefix='/especialidades')
    app.register_blueprint(comunicados_bp, url_prefix='/comunicados')
    app.register_blueprint(recursos_bp, url_prefix='/recursos')
    app.register_blueprint(cronograma_bp, url_prefix='/cronograma')
    app.register_blueprint(mensajeria_bp, url_prefix='/mensajeria')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    app.register_blueprint(configuracion_bp, url_prefix='/configuracion')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(valoraciones_bp, url_prefix='/valoraciones')
    app.register_blueprint(archivo_bp, url_prefix='/archivo')
    app.register_blueprint(parametrizacion_bp, url_prefix='/parametrizacion')
    app.register_blueprint(matricula_bp, url_prefix='/matricula')
    
    # Ruta pública de inicio
    @app.route("/")
    def inicio():
        from flask import render_template
        return render_template("pagina/index.html", page_title="Inicio", active_page="index")
    
    # Rutas públicas de información
    @app.route("/ques")
    def ques():
        from flask import render_template
        return render_template("pagina/QUES.html", page_title="¿Qué es ZOE?", active_page="ques")
    
    @app.route("/programa-pop")
    def programa_pop():
        from flask import render_template
        return render_template("pagina/ProgramaPOP.html", page_title="Programa POP", active_page="programa-pop")
    
    @app.route("/estructura")
    def estructura():
        from flask import render_template
        return render_template("pagina/estructura.html", page_title="Estructura Académica", active_page="estructura")
    
    # Ruta de health check
    @app.route("/health")
    def health():
        return {"status": "ok", "app": "ZOE"}, 200

    # Búsqueda global (usada por la barra superior de la aplicación)
    @app.route("/buscar")
    def buscar_global():
        from flask import request, jsonify
        from app.models import Tarea, Materia, Grupo, Curso, Especialidad, Recurso, Usuario, ProyectoArchivado

        texto = request.args.get("q", "").strip()
        if not session.get("usuario_id") or len(texto) < 2:
            return jsonify({"resultados": []})

        rol = session.get("rol")
        resultados = []

        for tarea in Tarea.buscar(texto):
            resultados.append({
                "tipo": "Tarea",
                "titulo": tarea.titulo,
                "subtitulo": tarea.materia_nombre or "Sin materia",
                "url": url_for("tareas.listar_tareas")
            })

        for materia in Materia.buscar(texto):
            resultados.append({
                "tipo": "Materia",
                "titulo": materia.nombre,
                "subtitulo": "Materia",
                "url": url_for("materias.listar_materias")
            })

        for grupo in Grupo.buscar(texto):
            resultados.append({
                "tipo": "Grupo",
                "titulo": grupo.nombre,
                "subtitulo": grupo.materia_nombre or "Sin materia",
                "url": url_for("grupos.listar_grupos")
            })

        for curso in Curso.buscar(texto):
            resultados.append({
                "tipo": "Curso",
                "titulo": str(curso.codigo),
                "subtitulo": curso.cohorte_nombre or "Sin cohorte",
                "url": url_for("cursos.listar_cursos")
            })

        for especialidad in Especialidad.buscar(texto):
            resultados.append({
                "tipo": "Especialidad",
                "titulo": especialidad.nombre,
                "subtitulo": "Especialidad",
                "url": url_for("especialidades.listar_especialidades")
            })

        for recurso in Recurso.buscar(texto):
            resultados.append({
                "tipo": "Recurso",
                "titulo": recurso.titulo,
                "subtitulo": (recurso.tipo or "recurso").capitalize(),
                "url": url_for("recursos.listar_recursos")
            })

        for proyecto in ProyectoArchivado.buscar(texto=texto, limite=5):
            resultados.append({
                "tipo": "Archivo",
                "titulo": proyecto.titulo,
                "subtitulo": proyecto.materia_nombre or proyecto.cohorte_nombre or "Proyecto archivado",
                "url": url_for("archivo.listar_archivo")
            })

        if rol == "coordinador":
            for usuario in Usuario.buscar(texto):
                resultados.append({
                    "tipo": "Usuario",
                    "titulo": usuario.nombre,
                    "subtitulo": usuario.correo,
                    "url": url_for("usuarios.listar_usuarios")
                })

        return jsonify({"resultados": resultados[:20]})

    return app