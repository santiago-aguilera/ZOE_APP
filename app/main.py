"""
ZOE — Rutas de la aplicación.
Se exporta register_routes() para ser usado desde __init__.py (factory pattern).
"""

import sys
from pathlib import Path
from flask import redirect, render_template, request, session, url_for
from config import Config

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _pagina(template, titulo, pagina_activa):
    return render_template(template, page_title=titulo, active_page=pagina_activa)


def _aplicacion(template, titulo, pagina_activa, **kwargs):
    defaults = {
        "rol": session.get("rol", "estudiante"),
        "usuario": session.get("usuario", "Usuario Demo"),
    }
    defaults.update(kwargs)
    return render_template(template, page_title=titulo, active_page=pagina_activa, **defaults)


def register_routes(app):
    """Registra todas las rutas en la aplicación Flask."""

    @app.context_processor
    def variables_globales():
        return {"app_name": "ZOE IB"}

    # -------------------------------------------------------------------------
    # Páginas públicas (templates/pagina/)
    # -------------------------------------------------------------------------
    @app.route("/")
    def inicio():
        return _pagina("pagina/index.html", "Inicio", "index")

    @app.route("/programa-pop")
    def programa_pop():
        return _pagina("pagina/ProgramaPOP.html", "Programa POP", "programa-pop")

    @app.route("/Estructura")
    def estructura():
        return _pagina("pagina/estructura.html", "Estructura", "estructura")

    @app.route("/ques")
    def ques():
        return _pagina("pagina/QUES.html", "¿Qué es ZOE?", "ques")

    # -------------------------------------------------------------------------
    # Aplicación interna (templates/aplicacion/)
    # -------------------------------------------------------------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "")
            if "coord" in email:
                session["rol"] = "coordinador"
            elif "prof" in email or "lic" in email:
                session["rol"] = "profesor"
            else:
                session["rol"] = "estudiante"
            session["usuario"] = email
            return redirect(url_for("dashboard"))
        return _aplicacion("aplicacion/auth/login.html", "Login", "login")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("inicio"))

    @app.route("/dashboard")
    def dashboard():
        return _aplicacion("aplicacion/dashboard.html", "Dashboard", "dashboard",
                          fecha="martes, 2 de junio de 2026")

    @app.route("/tareas")
    def tareas():
        return _aplicacion("aplicacion/usuarios/tareas.html", "Tareas", "tareas")

    @app.route("/mensajeria")
    def mensajeria():
        return _aplicacion("aplicacion/usuarios/mensajeria.html", "Mensajería", "mensajeria")

    @app.route("/cronograma")
    def cronograma():
        return _aplicacion("aplicacion/usuarios/cronograma.html", "Cronograma", "cronograma")

    @app.route("/recursos")
    def recursos():
        return _aplicacion("aplicacion/recursos/recursos.html", "Recursos Académicos", "recursos")

    @app.route("/informacion")
    def informacion():
        return _aplicacion("aplicacion/informacion/informacion.html", "Información", "informacion")

    @app.route("/reportes")
    def reportes():
        return _aplicacion("aplicacion/reportes/reportes.html", "Reportes", "reportes")

    @app.route("/materias")
    def materias():
        return _aplicacion("aplicacion/materias.html", "Materias", "materias")

    @app.route("/grupos")
    def grupos():
        return _aplicacion("aplicacion/grupos/grupos.html", "Grupos", "grupos")

    @app.route("/configuracion")
    def configuracion():
        return _aplicacion("aplicacion/config/configuracion.html", "Configuración", "configuracion")

    # -------------------------------------------------------------------------
    # Formularios CRUD
    # -------------------------------------------------------------------------
    @app.route("/formularios/crear-usuario")
    def form_crear_usuario():
        return _aplicacion("aplicacion/formularios/crear_usuario.html", "Crear Usuario", "usuarios")

    @app.route("/formularios/crear-materia")
    def form_crear_materia():
        return _aplicacion("aplicacion/formularios/crear_materia.html", "Crear Materia", "configuracion")

    @app.route("/formularios/crear-grupo")
    def form_crear_grupo():
        return _aplicacion("aplicacion/formularios/crear_grupo.html", "Crear Grupo", "configuracion")

    @app.route("/formularios/crear-tarea")
    def form_crear_tarea():
        return _aplicacion("aplicacion/formularios/crear_tarea.html", "Crear Tarea", "tareas")

    @app.route("/formularios/crear-recurso")
    def form_crear_recurso():
        return _aplicacion("aplicacion/formularios/crear_recurso.html", "Subir Recurso", "recursos")

    @app.route("/formularios/crear-periodo")
    def form_crear_periodo():
        return _aplicacion("aplicacion/formularios/crear_periodo.html", "Crear Período", "configuracion")

    # -------------------------------------------------------------------------
    # Gestión de usuarios
    # -------------------------------------------------------------------------
    @app.route("/usuarios")
    def usuarios_list():
        return _aplicacion("aplicacion/usuarios/usuarios.html", "Usuarios", "usuarios")

    @app.route("/usuarios/crear")
    def usuarios_create():
        return redirect(url_for("form_crear_usuario"))

    @app.route("/usuarios/editar/<int:id>")
    def usuarios_edit(id):
        return _aplicacion("aplicacion/usuarios/usuarios_edit.html", "Editar Usuario", "usuarios")

    @app.route("/usuarios/eliminar/<int:id>")
    def usuarios_delete(id):
        return _aplicacion("aplicacion/usuarios/usuarios_delete.html", "Eliminar Usuario", "usuarios")

    # -------------------------------------------------------------------------
    # Health check
    # -------------------------------------------------------------------------
    @app.route("/health")
    def health():
        return {"status": "ok", "app": "ZOE"}, 200


<<<<<<< HEAD
# Para arranque directo `python main.py` (sin DB)
=======


# -----------------------------------------------------------------------------
# Rutas de aplicación interna (templates/aplicacion/)
# -----------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Simulación: siempre entra como estudiante
        session["usuario"] = request.form["email"]
        session["rol"] = "estudiante"
        return redirect(url_for("dashboard"))
    # Renderiza la plantilla de login
    return _aplicacion("aplicacion/auth/login.html", "Login", "login")

@app.route("/dashboard")
def dashboard():
    rol = session.get("rol", "estudiante")   # valor por defecto
    usuario = session.get("usuario", "Usuario Demo")
    fecha = "martes, 2 de junio de 2026"

    return _aplicacion("aplicacion/dashboard.html", "Dashboard", "dashboard",usuario=usuario, rol=rol, fecha=fecha)

@app.route("/calendario")
def calendario():
    rol = session.get("rol", "estudiante")
    usuario = session.get("usuario", "Usuario Demo")
    fecha = "jueves, 4 de junio de 2026"

    # Datos falsos de ejemplo
    stats = dict(
        tareas_pendientes=2,
        eventos_proximos=6,
        tareas_completadas=0,
        mensajes_nuevos=3,
        grupos=4,
        entregas_pendientes=5,
        estudiantes_activos=312,
        profesores=28
    )

    # Simulación de calendario: lista de semanas con días
    calendario = [
        [{"numero": 25}, {"numero": 26}, {"numero": 27, "evento": True},
         {"numero": 28, "evento": True}, {"numero": 29}, {"numero": 30}, {"numero": 31}],
        [{"numero": 1}, {"numero": 2}, {"numero": 3}, {"numero": 4}, {"numero": 5}, {"numero": 6}, {"numero": 7}],
    ]

    proximos_eventos = [
        "Clase HPP — Reflexión grupal (2026-05-27 · 12:00)",
        "Proyecto Programación (2026-05-28 · 12:00)",
        "Entrega: Taller de ecuaciones (2026-05-29 · 12:00)",
        "Entrega: Análisis literario (2026-05-31 · 12:00)"
    ]

    return _aplicacion("aplicacion/cronograma.html", "Calendario", "calendario",
                       usuario=usuario, rol=rol, fecha=fecha,
                       calendario=calendario, proximos_eventos=proximos_eventos,
                       **stats)


@app.route("/materias")
def materias():
    rol = session.get("rol", "estudiante")
    usuario = session.get("usuario", "Usuario Demo")
    fecha = "jueves, 4 de junio de 2026"

    return _aplicacion("aplicacion/materias.html", "Materias", "materias",
                       usuario=usuario, rol=rol, fecha=fecha)

@app.route("/tareas")
def tareas():
    rol = session.get("rol", "estudiante")
    usuario = session.get("usuario", "Usuario Demo")

    # Datos falsos de ejemplo
    tareas = [
        {"materia": "Matemáticas", "titulo": "Ecuaciones Diferenciales — Capítulo 4",
         "responsable": "Fabián Tovar", "estado": "completada", "fecha": "2026-05-29"},
        {"materia": "Lengua y Literatura", "titulo": "Análisis literario — Realismo Mágico",
         "responsable": "Yolanda Forero", "estado": "pendiente", "fecha": "2026-05-31"},
        {"materia": "Proyecto de Reflexión", "titulo": "Ensayo final de reflexión",
         "responsable": "Paula Sandoval", "estado": "pendiente", "fecha": "2026-06-02"},
        {"materia": "HPP", "titulo": "Ensayo de Fortalezas",
         "responsable": "Diliana Sánchez", "estado": "pendiente", "fecha": "2026-06-05"},
        {"materia": "Ambiental", "titulo": "Ensayo sobre impacto ambiental",
         "responsable": "Eliana Gómez", "estado": "revision", "fecha": "2026-04-20"},
        {"materia": "Inglés", "titulo": "Práctica de Speaking",
         "responsable": "Jhaneht Becerra", "estado": "pendiente", "fecha": "2026-04-10"},
        {"materia": "Programación", "titulo": "Proyecto Web",
         "responsable": "José Santana", "estado": "pendiente", "fecha": "2026-06-10"},
    ]

    return _aplicacion("aplicacion/tareas.html", "Tareas", "tareas",
                       usuario=usuario, rol=rol, tareas=tareas)

@app.route("/recursos", methods=["GET", "POST"])
def recursos():
    rol = session.get("rol", "estudiante")
    usuario = session.get("usuario", "Usuario Demo")

    # Datos falsos de ejemplo
    recursos = [
        {"titulo": "Guía de estudio — Álgebra Vectorial", "materia": "Matemáticas", "tipo": "PDF", "tamano": "1.2 MB", "fecha": "2026-05-01"},
        {"titulo": "Lectura obligatoria — Realismo Mágico", "materia": "Lengua y Literatura", "tipo": "PDF", "tamano": "1.2 MB", "fecha": "2026-05-01"},
        {"titulo": "Manual de referencias APA 7a edición", "materia": "HPP", "tipo": "PDF", "tamano": "1.2 MB", "fecha": "2026-05-01"},
        {"titulo": "Guía para Proyecto de Reflexión", "materia": "Proyecto de Reflexión", "tipo": "PDF", "tamano": "1.2 MB", "fecha": "2026-05-01"},
        {"titulo": "Vocabulario de negocios", "materia": "Inglés", "tipo": "PDF", "tamano": "1.2 MB", "fecha": "2026-05-01"},
        {"titulo": "Guía para App Web", "materia": "Programación", "tipo": "PDF", "tamano": "1.2 MB", "fecha": "2026-05-01"},
    ]

    if request.method == "POST" and rol in ["coordinador", "profesor"]:
        # Aquí luego se manejará la subida real del archivo
        titulo = request.form["titulo"]
        materia = request.form["materia"]
        # archivo = request.files["archivo"]  # pendiente para BD
        recursos.append({"titulo": titulo, "materia": materia, "tipo": "PDF", "tamano": "X MB", "fecha": "2026-06-04"})

    return _aplicacion("aplicacion/recursos/recursos.html", "Recursos", "recursos",
                       usuario=usuario, rol=rol, recursos=recursos)

@app.route("/comunicados", methods=["GET", "POST"])
def comunicados():
    rol = session.get("rol", "estudiante")
    usuario = session.get("usuario", "Usuario Demo")

    # Datos falsos de ejemplo
    comunicados = [
        {"titulo": "Semana de Evaluaciones IB — Calendario definitivo (URGENTE)",
         "autor": "Coordinación Académica", "fecha": "2026-05-25",
         "texto": "La Semana de Evaluaciones Internas del programa IB se llevará a cabo del 2 al 13 de junio de 2026."},
        {"titulo": "Actualización: Plazos de entrega del Proyecto de Reflexión (Fijado)",
         "autor": "Dra. María González", "fecha": "2026-05-23",
         "texto": "Se han actualizado los plazos de entrega del Proyecto de Reflexión."},
        {"titulo": "Taller extracurricular: Preparación exámenes IB",
         "autor": "Dpto. Académico", "fecha": "2026-05-20",
         "texto": "Se invita a los estudiantes a participar en el taller de preparación para exámenes IB."},
    ]

    if request.method == "POST" and rol in ["coordinador", "profesor"]:
        titulo = request.form["titulo"]
        texto = request.form["texto"]
        comunicados.append({"titulo": titulo, "autor": usuario, "fecha": "2026-06-04", "texto": texto})

    return _aplicacion("aplicacion/reportes/comunicado.html", "Comunicados", "comunicados",
                       usuario=usuario, rol=rol, comunicados=comunicados)

@app.route("/administracion")
def administracion():
    rol = session.get("rol", "estudiante")
    usuario = session.get("usuario", "Usuario Demo")

    # Solo coordinador puede ver
    if rol != "coordinador":
        return "Acceso restringido", 403

    usuarios = [
        {"nombre": "Carlos Gil", "correo": "carlos@colegio.mx", "rol": "Coordinador", "estado": "Activo"},
        {"nombre": "Bibiana Sanchez", "correo": "bibiana@colegio.mx", "rol": "Profesor", "estado": "Activo"},
        {"nombre": "Juan Pérez", "correo": "juan@colegio.mx", "rol": "Estudiante", "estado": "Activo"},
    ]

    materias = [
        {"nombre": "HPP", "sector": "Troncal", "nivel": "", "estado": "Activa"},
        {"nombre": "Matemáticas", "sector": "IB", "nivel": "HL", "estado": "Activa"},
        {"nombre": "Programación", "sector": "Especialidad", "nivel": "", "estado": "Activa"},
    ]

    grupos = [
        {"nombre": "POP-A", "periodo": "2025–2026", "materia": "General", "estudiantes": 0},
        {"nombre": "IB-2A", "periodo": "2025–2026", "materia": "General", "estudiantes": 0},
    ]

    periodos = [
        {"nombre": "2024–2025", "inicio": "2024-08-19", "fin": "2025-06-15", "estado": "Cerrado"},
        {"nombre": "2025–2026", "inicio": "2025-08-18", "fin": "2026-06-14", "estado": "Activo"},
    ]

    return _aplicacion("aplicacion/config/configuracion.html", "Administración", "administracion",
                       usuario=usuario, rol=rol,
                       usuarios=usuarios, materias=materias, grupos=grupos, periodos=periodos)


@app.route("/chat", methods=["GET", "POST"])
def chat():
    rol = session.get("rol", "estudiante")
    usuario = session.get("usuario", "Usuario Demo")

    # Mensajes simulados
    mensajes = [
        {"titulo": "Recordatorio: Entrega Proyecto de Reflexión",
         "remitente": "Dra. María González", "destinatario": "Ana López García",
         "texto": "El plazo para la entrega vence este viernes 29 de mayo.",
         "fecha": "2026-05-27"},
        {"titulo": "Aviso: Taller de Matemáticas",
         "remitente": "Prof. Fabián Tovar", "destinatario": "Grupo IB-2A",
         "texto": "Se realizará un taller de ecuaciones el 29 de mayo.",
         "fecha": "2026-05-25"},
    ]

    if request.method == "POST":
        titulo = request.form["titulo"]
        destinatario = request.form["destinatario"]
        texto = request.form["texto"]
        mensajes.append({"titulo": titulo, "remitente": usuario,
                         "destinatario": destinatario, "texto": texto,
                         "fecha": "2026-06-04"})

    return _aplicacion("aplicacion/mensajeria.html", "Chat", "chat",
                       usuario=usuario, rol=rol, mensajes=mensajes)

@app.route("/informes")
def informes():
    rol = session.get("rol", "estudiante")
    usuario = session.get("usuario", "Usuario Demo")

    # Datos simulados según rol
    if rol == "coordinador":
        resumen = [
            {"titulo": "Estudiantes matriculados", "valor": 312},
            {"titulo": "Profesores activos", "valor": 28},
            {"titulo": "Tasa puntualidad", "valor": "75%"},
            {"titulo": "Estudiantes en riesgo", "valor": 23},
        ]
        materias = ["HPP", "Programación", "Matemáticas", "Lengua y Literatura"]
        entregas_tiempo = [40, 25, 20, 30]
        entregas_retraso = [5, 10, 2, 2]
        entregas_pendientes = [3, 4, 2, 0]
        global_tiempo, global_retraso, global_pendientes = 85, 19, 9

    elif rol == "profesor":
        resumen = [
            {"titulo": "Mis grupos", "valor": 4},
            {"titulo": "Tareas publicadas", "valor": 18},
            {"titulo": "Entregas pendientes", "valor": 27},
            {"titulo": "Mensajes nuevos", "valor": 5},
        ]
        materias = ["Programación", "Diseño"]
        entregas_tiempo = [12, 8]
        entregas_retraso = [3, 2]
        entregas_pendientes = [1, 2]
        global_tiempo, global_retraso, global_pendientes = 20, 5, 3

    else:  # estudiante
        resumen = [
            {"titulo": "Mis materias activas", "valor": 6},
            {"titulo": "Tareas pendientes", "valor": 12},
            {"titulo": "Entregas completadas", "valor": 34},
            {"titulo": "Promedio general", "valor": "8.4"},
        ]
        materias = ["Matemáticas", "Lengua y Literatura", "Inglés"]
        entregas_tiempo = [5, 6, 4]
        entregas_retraso = [1, 0, 2]
        entregas_pendientes = [2, 1, 0]
        global_tiempo, global_retraso, global_pendientes = 15, 3, 3

    return _aplicacion("aplicacion/reportes/reportes.html", "Informes", "informes",
                       usuario=usuario, rol=rol, resumen=resumen,
                       materias=materias,
                       entregas_tiempo=entregas_tiempo,
                       entregas_retraso=entregas_retraso,
                       entregas_pendientes=entregas_pendientes,
                       global_tiempo=global_tiempo,
                       global_retraso=global_retraso,
                       global_pendientes=global_pendientes)


# -----------------------------------------------------------------------------
# Rutas de gestión de usuarios (CRUD)
# -----------------------------------------------------------------------------
@app.route("/usuarios")
def usuarios_list():
    return _aplicacion("aplicacion/usuarios/usuarios.html", "Usuarios", "usuarios")

@app.route("/usuarios/crear")
def usuarios_create():
    return _aplicacion("aplicacion/usuarios/usuarios_create.html", "Crear Usuario", "usuarios")

@app.route("/usuarios/editar/<int:id>")
def usuarios_edit(id):
    return _aplicacion("aplicacion/usuarios/usuarios_edit.html", "Editar Usuario", "usuarios")

@app.route("/usuarios/eliminar/<int:id>")
def usuarios_delete(id):
    return _aplicacion("aplicacion/usuarios/usuarios_delete.html", "Eliminar Usuario", "usuarios")




# -----------------------------------------------------------------------------
# Arranque en desarrollo
# -----------------------------------------------------------------------------
>>>>>>> e4ccd826c7cda5b1e01ff5ce6d7d12c07996dbc3
if __name__ == "__main__":
    from flask import Flask
    _app = Flask(
        __name__,
        template_folder=str(Config.TEMPLATES_FOLDER),
        static_folder=str(Config.STATIC_FOLDER),
        static_url_path="/static",
    )
    _app.config.from_object(Config)
    _app.secret_key = Config.SECRET_KEY
    register_routes(_app)
    _app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)