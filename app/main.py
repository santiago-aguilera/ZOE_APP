import sys
from pathlib import Path
from datetime import datetime
from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app.config_db import DevelopmentConfig
from app.models import (
    db, Usuario, Materia, Grupo, Tarea, Entrega, 
    Recurso, Cronograma, Mensaje, Comunicado, PeriodoAcademico
)

# =====================================================================
# RUTAS Y CONFIGURACIÓN INICIAL
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent       # ZOE_APP/app/
PROJECT_ROOT = BASE_DIR.parent                  # ZOE_APP/

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# =====================================================================
# INICIALIZACIÓN DE FLASK Y SQLALCHEMY
# =====================================================================
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
    static_url_path="/static",
)

# Cargar configuración
app.config.from_object(DevelopmentConfig)

# Inicializar SQLAlchemy
db.init_app(app)



# =====================================================================
# CREAR TABLAS Y DATOS INICIALES
# =====================================================================
def init_db():
    """Inicializa la BD con datos de ejemplo si está vacía."""
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Si la BD está vacía, cargar datos de ejemplo
        if Usuario.query.first() is None:
            # Crear períodos
            periodo1 = PeriodoAcademico(
                nombre="Período I 2026",
                fecha_inicio="2026-01-15",
                fecha_fin="2026-05-30",
                activo=True
            )
            periodo2 = PeriodoAcademico(
                nombre="Período II 2026",
                fecha_inicio="2026-06-01",
                fecha_fin="2026-10-31",
                activo=True
            )
            db.session.add_all([periodo1, periodo2])
            db.session.commit()
            
            # Crear usuarios (con contraseñas hasheadas)
            usuario1 = Usuario(
                nombre="Juan Pérez",
                correo="juan@example.com",
                contrasena_hash=generate_password_hash("pass123"),
                rol="estudiante",
                periodo_id=periodo1.id,
                activo=True
            )
            usuario2 = Usuario(
                nombre="María García",
                correo="maria@example.com",
                contrasena_hash=generate_password_hash("pass123"),
                rol="profesor",
                periodo_id=periodo1.id,
                activo=True
            )
            usuario3 = Usuario(
                nombre="Carlos Martínez",
                correo="carlos@example.com",
                contrasena_hash=generate_password_hash("pass123"),
                rol="coordinador",
                periodo_id=periodo1.id,
                activo=True
            )
            usuario4 = Usuario(
                nombre="Ana López",
                correo="ana@example.com",
                contrasena_hash=generate_password_hash("pass123"),
                rol="estudiante",
                periodo_id=periodo1.id,
                activo=True
            )
            db.session.add_all([usuario1, usuario2, usuario3, usuario4])
            db.session.commit()
            
            # Crear materias
            materia1 = Materia(
                nombre="Matemáticas",
                descripcion="Cálculo y álgebra",
                periodo_id=periodo1.id
            )
            materia2 = Materia(
                nombre="Inglés",
                descripcion="Lengua inglesa avanzada",
                periodo_id=periodo1.id
            )
            materia3 = Materia(
                nombre="Física",
                descripcion="Cinemática y dinámica",
                periodo_id=periodo1.id
            )
            db.session.add_all([materia1, materia2, materia3])
            db.session.commit()
            
            # Crear grupos
            grupo1 = Grupo(
                nombre="Matemáticas A",
                descripcion="Grupo avanzado",
                materia_id=materia1.id,
                creado_por=usuario2.id
            )
            grupo2 = Grupo(
                nombre="Inglés B",
                descripcion="Grupo intermedio",
                materia_id=materia2.id,
                creado_por=usuario2.id
            )
            db.session.add_all([grupo1, grupo2])
            db.session.commit()
            
            # Agregar estudiantes a grupos
            grupo1.estudiantes.append(usuario1)
            grupo1.estudiantes.append(usuario4)
            grupo2.estudiantes.append(usuario1)
            db.session.commit()
            
            # Crear tareas
            tarea1 = Tarea(
                titulo="Ejercicios de cálculo",
                instrucciones="Resolver 10 ejercicios del capítulo 5",
                fecha_limite="2026-06-20",
                materia_id=materia1.id,
                creado_por=usuario2.id
            )
            tarea2 = Tarea(
                titulo="Ensayo en inglés",
                instrucciones="Escribir ensayo de 500 palabras sobre el cambio climático",
                fecha_limite="2026-06-25",
                materia_id=materia2.id,
                creado_por=usuario2.id
            )
            db.session.add_all([tarea1, tarea2])
            db.session.commit()
            
            print("✅ Base de datos inicializada con datos de ejemplo")



# =====================================================================
# DECORADOR PARA REQUERIR AUTENTICACIÓN
# =====================================================================
def login_required(f):
    """Decorador para proteger rutas que requieren autenticación."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# =====================================================================
# VARIABLES GLOBALES PARA TEMPLATES (JINJA2)
# =====================================================================
@app.context_processor
def variables_globales():
    return {
        "app_name": "ZOE IB",
        "usuario_id": session.get("usuario_id"),
        "usuario": session.get("usuario", "Usuario Demo"),
        "rol": session.get("rol", "invitado"),
    }


# =====================================================================
# FUNCIONES HELPERS PARA RENDERIZAR
# =====================================================================
def _pagina(template, titulo, pagina_activa):
    """Renderiza una página pública (sin requerir autenticación)."""
    return render_template(
        template,
        page_title=titulo,
        active_page=pagina_activa,
    )
    
def _aplicacion(template, titulo, pagina_activa, **kwargs):
    """Renderiza una página de la aplicación (con contexto de usuario)."""
    defaults = {
        "rol": session.get("rol", "estudiante"),
        "usuario": session.get("usuario", "Usuario Demo"),
        "usuario_id": session.get("usuario_id"),
    }
    defaults.update(kwargs)
    return render_template(
        template,
        page_title=titulo,
        active_page=pagina_activa,
        **defaults
    )


# =====================================================================
# RUTAS PÚBLICAS
# =====================================================================
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


# =====================================================================
# RUTAS DE AUTENTICACIÓN
# =====================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    """Login usando SQLAlchemy."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        # Buscar usuario en la BD
        usuario_encontrado = Usuario.query.filter_by(correo=email).first()
        
        if usuario_encontrado and check_password_hash(usuario_encontrado.contrasena_hash, password):
            # Guardar en sesión
            session['usuario_id'] = usuario_encontrado.id
            session['usuario'] = usuario_encontrado.nombre
            session['correo'] = usuario_encontrado.correo
            session['rol'] = usuario_encontrado.rol
            session.permanent = True
            return redirect(url_for("dashboard"))
        else:
            error = "Credenciales inválidas"
        
        return _aplicacion(
            "aplicacion/auth/login.html",
            "Login",
            "login",
            error_mensaje=error
        )
    
    return _aplicacion("aplicacion/auth/login.html", "Login", "login")


@app.route("/logout")
def logout():
    """Cierra la sesión del usuario."""
    session.clear()
    return redirect(url_for("inicio"))


# =====================================================================
# RUTAS DE APLICACIÓN INTERNA
# =====================================================================
@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard principal con datos de la BD."""
    usuario_id = session.get("usuario_id")
    usuario = session.get("usuario", "Usuario Demo")
    rol = session.get("rol", "estudiante")
    fecha = datetime.now().strftime("%A, %d de %B de %Y").replace('Monday', 'Lunes').replace('Tuesday', 'Martes').replace('Wednesday', 'Miércoles').replace('Thursday', 'Jueves').replace('Friday', 'Viernes').replace('Saturday', 'Sábado').replace('Sunday', 'Domingo').replace(' January ', ' enero ').replace(' February ', ' febrero ').replace(' March ', ' marzo ').replace(' April ', ' abril ').replace(' May ', ' mayo ').replace(' June ', ' junio ').replace(' July ', ' julio ').replace(' August ', ' agosto ').replace(' September ', ' septiembre ').replace(' October ', ' octubre ').replace(' November ', ' noviembre ').replace(' December ', ' diciembre ')
    
    contexto = {
        "usuario": usuario,
        "usuario_id": usuario_id,
        "rol": rol,
        "fecha": fecha,
    }
    
    # Estadísticas según el rol
    if rol == "estudiante":
        usuario_obj = Usuario.query.get(usuario_id)
        if usuario_obj:
            # Materias del estudiante
            contexto['mis_materias'] = len(usuario_obj.materias)
            
            # Tareas pendientes (entregas no completadas)
            tareas_pendientes = 0
            for entrega in usuario_obj.entregas:
                if entrega.estado != "entregado":
                    tareas_pendientes += 1
            contexto['mis_tareas'] = tareas_pendientes
    
    elif rol == "profesor":
        contexto['mis_tareas'] = Tarea.query.filter_by(creado_por=usuario_id).count()
        contexto['mis_grupos'] = Grupo.query.filter_by(creado_por=usuario_id).count()
    
    elif rol == "coordinador":
        contexto['usuarios_total'] = Usuario.query.count()
        contexto['materias_total'] = Materia.query.count()
        contexto['grupos_total'] = Grupo.query.count()

    return _aplicacion("aplicacion/dashboard.html", "Dashboard", "dashboard", **contexto)


@app.route("/tareas")
@login_required
def tareas():
    """Muestra tareas de la BD."""
    usuario_id = session.get("usuario_id")
    tareas_lista = []
    
    # Obtener tareas de la BD
    for tarea in Tarea.query.all():
        tareas_lista.append({
            'id': tarea.id,
            'titulo': tarea.titulo,
            'materia': tarea.materia.nombre if tarea.materia else "Sin asignar",
            'fecha_limite': tarea.fecha_limite.isoformat() if tarea.fecha_limite else "",
            'creador': tarea.creador.nombre if tarea.creador else "Sistema",
            'entregas': len(tarea.entregas),
        })
    
    return _aplicacion(
        "aplicacion/usuarios/tareas.html",
        "Tareas",
        "tareas",
        tareas=tareas_lista
    )


@app.route("/mensajeria")
@login_required
def mensajeria():
    """Muestra mensajes de la BD."""
    usuario_id = session.get("usuario_id")
    
    # Filtrar mensajes recibidos y enviados
    mensajes_recibidos = []
    for msg in Mensaje.query.filter_by(destinatario_id=usuario_id).all():
        mensajes_recibidos.append({
            'id': msg.id,
            'remitente': msg.remitente.nombre if msg.remitente else "Sistema",
            'asunto': msg.asunto,
            'leido': msg.leido,
        })
    
    mensajes_enviados = []
    for msg in Mensaje.query.filter_by(remitente_id=usuario_id).all():
        mensajes_enviados.append({
            'id': msg.id,
            'destinatario': msg.destinatario.nombre if msg.destinatario else "Sistema",
            'asunto': msg.asunto,
        })
    
    return _aplicacion(
        "aplicacion/usuarios/mensajeria.html",
        "Mensajería",
        "mensajeria",
        mensajes_recibidos=mensajes_recibidos,
        mensajes_enviados=mensajes_enviados
    )


@app.route("/cronograma")
@login_required
def cronograma():
    """Muestra cronograma de la BD."""
    proximos_eventos = []
    
    for evento in Cronograma.query.all():
        proximos_eventos.append({
            'id': evento.id,
            'titulo': evento.titulo,
            'descripcion': evento.descripcion,
            'fecha': evento.fecha_evento.isoformat() if evento.fecha_evento else "",
            'materia': evento.materia.nombre if evento.materia else "Sin asignar",
        })
    
    return _aplicacion(
        "aplicacion/usuarios/cronograma.html",
        "Cronograma",
        "cronograma",
        eventos=proximos_eventos
    )


@app.route("/recursos")
@login_required
def recursos():
    """Muestra recursos de la BD."""
    recursos_lista = []
    
    for recurso in Recurso.query.all():
        recursos_lista.append({
            'id': recurso.id,
            'titulo': recurso.titulo,
            'tipo': recurso.tipo,
            'materia': recurso.materia.nombre if recurso.materia else "Sin asignar",
            'autor': recurso.creador.nombre if recurso.creador else "Sistema",
        })
    
    return _aplicacion(
        "aplicacion/recursos/recursos.html",
        "Recursos Académicos",
        "recursos",
        recursos=recursos_lista
    )


@app.route("/informacion")
@login_required
def informacion():
    """Muestra comunicados de la BD."""
    comunicados = []
    
    for com in Comunicado.query.filter_by(activo=True).all():
        comunicados.append({
            'id': com.id,
            'titulo': com.titulo,
            'contenido': com.contenido,
            'autor': com.autor.nombre if com.autor else "Sistema",
            'fecha': com.publicado_en.strftime("%Y-%m-%d") if com.publicado_en else "",
        })
    
    return _aplicacion(
        "aplicacion/informacion/informacion.html",
        "Información",
        "informacion",
        comunicados=comunicados
    )


@app.route("/reportes")
@login_required
def reportes():
    """Muestra reportes."""
    return _aplicacion(
        "aplicacion/reportes/reportes.html",
        "Reportes",
        "reportes"
    )


@app.route("/materias")
@login_required
def materias():
    """Muestra materias de la BD."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol", "estudiante")
    
    materias_lista = []
    
    if rol == "estudiante":
        # Mostrar solo las materias del estudiante
        usuario = Usuario.query.get(usuario_id)
        materias_query = usuario.materias if usuario else []
    else:
        # Mostrar todas las materias
        materias_query = Materia.query.all()
    
    for materia in materias_query:
        materias_lista.append({
            'id': materia.id,
            'nombre': materia.nombre,
            'descripcion': materia.descripcion,
            'periodo': materia.periodo.nombre if materia.periodo else "Sin asignar",
            'profesores': sum(1 for g in materia.grupos for p in g.creador.materias if p.id == materia.id),
            'grupos': len(materia.grupos),
            'tareas': len(materia.tareas),
        })
    
    return _aplicacion(
        "aplicacion/materias.html",
        "Materias",
        "materias",
        materias=materias_lista
    )


@app.route("/grupos")
@login_required
def grupos():
    """Muestra grupos de la BD."""
    grupos_lista = []
    
    for grupo in Grupo.query.all():
        grupos_lista.append({
            'id': grupo.id,
            'nombre': grupo.nombre,
            'descripcion': grupo.descripcion,
            'materia': grupo.materia.nombre if grupo.materia else "Sin asignar",
            'profesor': grupo.creador.nombre if grupo.creador else "Sistema",
            'estudiantes': len(grupo.estudiantes),
        })
    
    return _aplicacion(
        "aplicacion/grupos/grupos.html",
        "Grupos",
        "grupos",
        grupos=grupos_lista
    )


@app.route("/configuracion")
@login_required
def configuracion():
    """Muestra página de configuración."""
    return _aplicacion(
        "aplicacion/config/configuracion.html",
        "Configuración",
        "configuracion"
    )


# =====================================================================
# RUTAS DE FORMULARIOS CRUD
# =====================================================================
@app.route("/formularios/crear-usuario", methods=["GET", "POST"])
@login_required
def form_crear_usuario():
    """Crear usuario."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        contrasena = request.form.get("contrasena", "").strip()
        rol = request.form.get("rol", "estudiante")
        
        # Verificar que el correo no exista
        if Usuario.query.filter_by(correo=correo).first():
            return _aplicacion(
                "aplicacion/formularios/crear_usuario.html",
                "Crear Usuario",
                "usuarios",
                error_mensaje="El correo ya está registrado"
            )
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            contrasena_hash=generate_password_hash(contrasena),
            rol=rol,
            activo=True
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return redirect(url_for("usuarios_list"))
    
    return _aplicacion(
        "aplicacion/formularios/crear_usuario.html",
        "Crear Usuario",
        "usuarios"
    )


@app.route("/formularios/crear-materia", methods=["GET", "POST"])
@login_required
def form_crear_materia():
    """Crear materia."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        periodo_id = request.form.get("periodo_id", 1, type=int)
        
        # Encontrar el período
        periodo = PeriodoAcademico.query.get(periodo_id)
        
        if not periodo:
            periodos = [{"id": p.id, "nombre": p.nombre} for p in PeriodoAcademico.query.all()]
            return _aplicacion(
                "aplicacion/formularios/crear_materia.html",
                "Crear Materia",
                "configuracion",
                error_mensaje="Período no encontrado",
                periodos=periodos
            )
        
        # Crear nueva materia
        nueva_materia = Materia(
            nombre=nombre,
            descripcion=descripcion,
            periodo_id=periodo_id
        )
        db.session.add(nueva_materia)
        db.session.commit()
        
        return redirect(url_for("materias"))
    
    periodos = [{"id": p.id, "nombre": p.nombre} for p in PeriodoAcademico.query.all()]
    return _aplicacion(
        "aplicacion/formularios/crear_materia.html",
        "Crear Materia",
        "configuracion",
        periodos=periodos
    )


@app.route("/formularios/crear-grupo", methods=["GET", "POST"])
@login_required
def form_crear_grupo():
    """Crear grupo."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        materia_id = request.form.get("materia_id", 1, type=int)
        profesor_id = request.form.get("profesor_id", 1, type=int)
        
        # Encontrar materia y profesor
        materia = Materia.query.get(materia_id)
        profesor = Usuario.query.get(profesor_id)
        
        if not materia or not profesor:
            materias = [{"id": m.id, "nombre": m.nombre} for m in Materia.query.all()]
            usuarios = [{"id": u.id, "nombre": u.nombre} for u in Usuario.query.all()]
            return _aplicacion(
                "aplicacion/formularios/crear_grupo.html",
                "Crear Grupo",
                "configuracion",
                error_mensaje="Materia o profesor no encontrado",
                materias=materias,
                usuarios=usuarios
            )
        
        # Crear nuevo grupo
        nuevo_grupo = Grupo(
            nombre=nombre,
            descripcion=descripcion,
            materia_id=materia_id,
            creado_por=profesor_id
        )
        db.session.add(nuevo_grupo)
        db.session.commit()
        
        return redirect(url_for("grupos"))
    
    materias = [{"id": m.id, "nombre": m.nombre} for m in Materia.query.all()]
    usuarios = [{"id": u.id, "nombre": u.nombre} for u in Usuario.query.all()]
    return _aplicacion(
        "aplicacion/formularios/crear_grupo.html",
        "Crear Grupo",
        "configuracion",
        materias=materias,
        usuarios=usuarios
    )


@app.route("/formularios/crear-tarea", methods=["GET", "POST"])
@login_required
def form_crear_tarea():
    """Crear tarea."""
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        instrucciones = request.form.get("instrucciones", "").strip()
        fecha_limite = request.form.get("fecha_limite", "")
        materia_id = request.form.get("materia_id", 1, type=int)
        usuario_id = session.get("usuario_id", 1)
        
        # Encontrar materia
        materia = Materia.query.get(materia_id)
        
        if not materia:
            materias = [{"id": m.id, "nombre": m.nombre} for m in Materia.query.all()]
            return _aplicacion(
                "aplicacion/formularios/crear_tarea.html",
                "Crear Tarea",
                "tareas",
                error_mensaje="Materia no encontrada",
                materias=materias
            )
        
        try:
            # Crear nueva tarea
            nueva_tarea = Tarea(
                titulo=titulo,
                instrucciones=instrucciones,
                fecha_limite=fecha_limite if fecha_limite else None,
                materia_id=materia_id,
                creado_por=usuario_id
            )
            db.session.add(nueva_tarea)
            db.session.commit()
            
            return redirect(url_for("tareas"))
        except Exception as e:
            materias = [{"id": m.id, "nombre": m.nombre} for m in Materia.query.all()]
            return _aplicacion(
                "aplicacion/formularios/crear_tarea.html",
                "Crear Tarea",
                "tareas",
                error_mensaje=str(e),
                materias=materias
            )
    
    materias = [{"id": m.id, "nombre": m.nombre} for m in Materia.query.all()]
    return _aplicacion(
        "aplicacion/formularios/crear_tarea.html",
        "Crear Tarea",
        "tareas",
        materias=materias
    )


@app.route("/formularios/crear-recurso", methods=["GET", "POST"])
@login_required
def form_crear_recurso():
    """Crear recurso."""
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        url_archivo = request.form.get("url_archivo", "").strip()
        tipo = request.form.get("tipo", "documento")
        materia_id = request.form.get("materia_id", 1, type=int)
        usuario_id = session.get("usuario_id", 1)
        
        # Encontrar materia
        materia = Materia.query.get(materia_id)
        
        if not materia:
            materias = [{"id": m.id, "nombre": m.nombre} for m in Materia.query.all()]
            return _aplicacion(
                "aplicacion/formularios/crear_recurso.html",
                "Subir Recurso",
                "recursos",
                error_mensaje="Materia no encontrada",
                materias=materias
            )
        
        # Crear nuevo recurso
        nuevo_recurso = Recurso(
            titulo=titulo,
            descripcion=descripcion,
            url_archivo=url_archivo,
            tipo=tipo,
            materia_id=materia_id,
            creado_por=usuario_id
        )
        db.session.add(nuevo_recurso)
        db.session.commit()
        
        return redirect(url_for("recursos"))
    
    materias = [{"id": m.id, "nombre": m.nombre} for m in Materia.query.all()]
    return _aplicacion(
        "aplicacion/formularios/crear_recurso.html",
        "Subir Recurso",
        "recursos",
        materias=materias
    )


@app.route("/formularios/crear-periodo", methods=["GET", "POST"])
@login_required
def form_crear_periodo():
    """Crear período académico."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        fecha_inicio = request.form.get("fecha_inicio", "")
        fecha_fin = request.form.get("fecha_fin", "")
        
        try:
            nuevo_periodo = PeriodoAcademico(
                nombre=nombre,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                activo=True
            )
            db.session.add(nuevo_periodo)
            db.session.commit()
            return redirect(url_for("configuracion"))
        except Exception as e:
            return _aplicacion(
                "aplicacion/formularios/crear_periodo.html",
                "Crear Período",
                "configuracion",
                error_mensaje=str(e)
            )
    
    return _aplicacion(
        "aplicacion/formularios/crear_periodo.html",
        "Crear Período",
        "configuracion"
    )


# =====================================================================
# RUTAS DE GESTIÓN DE USUARIOS (CRUD)
# =====================================================================
@app.route("/usuarios")
@login_required
def usuarios_list():
    """Lista usuarios."""
    usuarios_lista = []
    for u in Usuario.query.all():
        usuarios_lista.append({
            'id': u.id,
            'nombre': u.nombre,
            'correo': u.correo,
            'rol': u.rol
        })
    
    return _aplicacion(
        "aplicacion/usuarios/usuarios.html",
        "Usuarios",
        "usuarios",
        usuarios=usuarios_lista
    )


@app.route("/usuarios/crear")
@login_required
def usuarios_create():
    """Redirige al formulario de crear usuario."""
    return redirect(url_for("form_crear_usuario"))


@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
@login_required
def usuarios_edit(id):
    """Edita un usuario existente."""
    usuario = Usuario.query.get(id)
    
    if not usuario:
        return redirect(url_for("usuarios_list"))
    
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        rol = request.form.get("rol", "estudiante")
        
        # Actualizar
        usuario.nombre = nombre
        usuario.correo = correo
        usuario.rol = rol
        db.session.commit()
        
        return redirect(url_for("usuarios_list"))
    
    return _aplicacion(
        "aplicacion/usuarios/usuarios_edit.html",
        "Editar Usuario",
        "usuarios",
        usuario={
            'id': usuario.id,
            'nombre': usuario.nombre,
            'correo': usuario.correo,
            'rol': usuario.rol
        }
    )


@app.route("/usuarios/eliminar/<int:id>", methods=["POST"])
@login_required
def usuarios_delete(id):
    """Elimina un usuario."""
    usuario = Usuario.query.get(id)
    
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
    
    return redirect(url_for("usuarios_list"))


# =====================================================================
# API REST AUXILIAR
# =====================================================================
@app.route("/api/materias")
def api_materias():
    """API para obtener materias en JSON."""
    materias_json = []
    for m in Materia.query.all():
        materias_json.append({
            'id': m.id,
            'nombre': m.nombre,
            'descripcion': m.descripcion,
        })
    return jsonify(materias_json)


@app.route("/api/grupos/<int:materia_id>")
def api_grupos_por_materia(materia_id):
    """API para obtener grupos de una materia."""
    grupos_json = []
    for g in Grupo.query.filter_by(materia_id=materia_id).all():
        grupos_json.append({
            'id': g.id,
            'nombre': g.nombre,
        })
    return jsonify(grupos_json)


@app.route("/api/usuarios")
def api_usuarios():
    """API para obtener usuarios en JSON."""
    usuarios_json = []
    for u in Usuario.query.all():
        usuarios_json.append({
            'id': u.id,
            'nombre': u.nombre,
            'rol': u.rol
        })
    return jsonify(usuarios_json)


# =====================================================================
# HEALTH CHECK
# =====================================================================
@app.route("/health")
def health():
    return {"status": "ok", "app": "ZOE"}, 200


# =====================================================================
# ARRANQUE
# =====================================================================
if __name__ == "__main__":
    init_db()  # Inicializar BD con tablas y datos
    app.run(host="127.0.0.1", port=5000, debug=True)

