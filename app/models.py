"""
Modelos SQLAlchemy para ZOE.
Mapean las 13 tablas de la BD MySQL a objetos Python.
Estos modelos coinciden exactamente con el esquema existente en XAMPP.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instancia de SQLAlchemy (será inicializada en main.py)
db = SQLAlchemy()


# ============================================================================
# TABLAS PRINCIPALES
# ============================================================================

class PeriodoAcademico(db.Model):
    """Período académico (semestre, año escolar, etc)."""
    __tablename__ = 'periodo_academico'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=True)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)
    activo = db.Column(db.Boolean, nullable=True, default=True)
    
    # Relaciones
    usuarios = db.relationship('Usuario', backref='periodo', lazy=True)
    materias = db.relationship('Materia', backref='periodo', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<PeriodoAcademico {self.nombre}>"


class Usuario(db.Model):
    """Usuarios del sistema (estudiantes, profesores, coordinadores)."""
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=True)
    correo = db.Column(db.String(255), nullable=True, unique=True)
    contrasena_hash = db.Column(db.String(255), nullable=True)
    rol = db.Column(db.String(50), nullable=True)  # 'estudiante', 'profesor', 'coordinador', 'admin'
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodo_academico.id'), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    activo = db.Column(db.Boolean, nullable=True, default=True)
    
    # Relaciones
    tareas_creadas = db.relationship('Tarea', backref='creador', lazy=True, cascade='all, delete-orphan', foreign_keys='Tarea.creado_por')
    recursos_creados = db.relationship('Recurso', backref='creador', lazy=True, cascade='all, delete-orphan', foreign_keys='Recurso.creado_por')
    cronogramas_creados = db.relationship('Cronograma', backref='creador', lazy=True, cascade='all, delete-orphan', foreign_keys='Cronograma.creado_por')
    grupos_creados = db.relationship('Grupo', backref='creador', lazy=True, cascade='all, delete-orphan', foreign_keys='Grupo.creado_por')
    comunicados = db.relationship('Comunicado', backref='autor', lazy=True, cascade='all, delete-orphan', foreign_keys='Comunicado.creado_por')
    
    # Relaciones many-to-many
    materias = db.relationship('Materia', secondary='profesor_materia', backref='profesores', lazy=True)
    grupos = db.relationship('Grupo', secondary='estudiante_grupo', backref='estudiantes', lazy=True)
    
    # Mensajes
    mensajes_enviados = db.relationship('Mensaje', backref='remitente', lazy=True, cascade='all, delete-orphan', foreign_keys='Mensaje.remitente_id')
    mensajes_recibidos = db.relationship('Mensaje', backref='destinatario', lazy=True, cascade='all, delete-orphan', foreign_keys='Mensaje.destinatario_id')
    
    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.rol})>"


class Materia(db.Model):
    """Materias/Asignaturas del programa IB."""
    __tablename__ = 'materia'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodo_academico.id'), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relaciones
    grupos = db.relationship('Grupo', backref='materia', lazy=True, cascade='all, delete-orphan')
    tareas = db.relationship('Tarea', backref='materia', lazy=True, cascade='all, delete-orphan')
    recursos = db.relationship('Recurso', backref='materia', lazy=True, cascade='all, delete-orphan')
    cronogramas = db.relationship('Cronograma', backref='materia', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Materia {self.nombre}>"


class Grupo(db.Model):
    """Grupos de estudiantes en una materia."""
    __tablename__ = 'grupo'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Grupo {self.nombre}>"


class Tarea(db.Model):
    """Tareas/Asignaciones para estudiantes."""
    __tablename__ = 'tarea'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=True)
    instrucciones = db.Column(db.Text, nullable=True)
    fecha_limite = db.Column(db.Date, nullable=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relaciones
    entregas = db.relationship('Entrega', backref='tarea', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Tarea {self.titulo}>"


class Entrega(db.Model):
    """Entregas de tareas por estudiantes."""
    __tablename__ = 'entrega'
    
    id = db.Column(db.Integer, primary_key=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tarea.id'), nullable=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    archivo_url = db.Column(db.String(255), nullable=True)
    fecha_entrega = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.String(50), nullable=True)  # 'pendiente', 'entregado', 'calificado'
    calificacion = db.Column(db.String(50), nullable=True)
    comentario_profesor = db.Column(db.Text, nullable=True)
    
    # Relaciones
    estudiante = db.relationship('Usuario', backref='entregas', foreign_keys=[estudiante_id])
    
    def __repr__(self):
        return f"<Entrega Tarea#{self.tarea_id}>"


class Recurso(db.Model):
    """Recursos educativos (archivos, enlaces, etc)."""
    __tablename__ = 'recurso'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    url_archivo = db.Column(db.String(255), nullable=True)
    tipo = db.Column(db.String(50), nullable=True)  # 'pdf', 'video', 'enlace', 'documento', etc
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Recurso {self.titulo}>"


class Cronograma(db.Model):
    """Eventos del cronograma/calendario de la materia."""
    __tablename__ = 'cronograma'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_evento = db.Column(db.Date, nullable=True)
    tipo = db.Column(db.String(50), nullable=True)  # 'clase', 'examen', 'entrega', etc
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Cronograma {self.titulo}>"


class Mensaje(db.Model):
    """Sistema de mensajería interna."""
    __tablename__ = 'mensaje'
    
    id = db.Column(db.Integer, primary_key=True)
    remitente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    asunto = db.Column(db.String(255), nullable=True)
    cuerpo = db.Column(db.Text, nullable=True)
    enviado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    leido = db.Column(db.Boolean, nullable=True, default=False)
    eliminado_remitente = db.Column(db.Boolean, nullable=True, default=False)
    eliminado_destinatario = db.Column(db.Boolean, nullable=True, default=False)
    
    def __repr__(self):
        return f"<Mensaje {self.asunto}>"


class Comunicado(db.Model):
    """Comunicados/Anuncios para toda la comunidad."""
    __tablename__ = 'comunicado'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=True)
    contenido = db.Column(db.Text, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    publicado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    activo = db.Column(db.Boolean, nullable=True, default=True)
    
    def __repr__(self):
        return f"<Comunicado {self.titulo}>"


# ============================================================================
# TABLAS DE RELACIONES MANY-TO-MANY
# ============================================================================

# Tabla de relación: profesor_materia
profesor_materia = db.Table(
    'profesor_materia',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), nullable=True),
    db.Column('materia_id', db.Integer, db.ForeignKey('materia.id'), nullable=True)
)

# Tabla de relación: estudiante_grupo
estudiante_grupo = db.Table(
    'estudiante_grupo',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), nullable=True),
    db.Column('grupo_id', db.Integer, db.ForeignKey('grupo.id'), nullable=True),
    db.Column('unido_en', db.DateTime, nullable=False, default=datetime.utcnow)
)

# Tabla de relación: estudiante_materia
estudiante_materia = db.Table(
    'estudiante_materia',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), nullable=True),
    db.Column('materia_id', db.Integer, db.ForeignKey('materia.id'), nullable=True),
    db.Column('inscrito_en', db.DateTime, nullable=False, default=datetime.utcnow)
)
