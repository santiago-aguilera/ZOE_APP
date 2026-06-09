"""
ZOE — Modelos SQLAlchemy para MySQL (XAMPP).
Mapea todas las tablas del esquema relacional.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class PeriodoAcademico(db.Model):
    __tablename__ = 'periodo_academico'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    usuarios = db.relationship('Usuario', backref='periodo', lazy=True)
    materias = db.relationship('Materia', backref='periodo', lazy=True)

    def __repr__(self):
        return f'<Periodo {self.nombre}>'


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('estudiante', 'profesor', 'coordinador'), nullable=False, default='estudiante')
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodo_academico.id'))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    activo = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.contrasena_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasena_hash, password)

    def __repr__(self):
        return f'<Usuario {self.nombre} ({self.rol})>'


class Materia(db.Model):
    __tablename__ = 'materia'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.Enum('regular', 'troncal'), nullable=False, default='regular')
    descripcion = db.Column(db.Text)
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodo_academico.id'))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    tareas = db.relationship('Tarea', backref='materia', lazy=True)
    recursos = db.relationship('Recurso', backref='materia', lazy=True)
    grupos = db.relationship('Grupo', backref='materia', lazy=True)

    def __repr__(self):
        return f'<Materia {self.nombre} ({self.tipo})>'


class ProfesorMateria(db.Model):
    __tablename__ = 'profesor_materia'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)


class EstudianteMateria(db.Model):
    __tablename__ = 'estudiante_materia'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)
    inscrito_en = db.Column(db.DateTime, default=datetime.utcnow)


class Tarea(db.Model):
    __tablename__ = 'tarea'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    instrucciones = db.Column(db.Text)
    fecha_limite = db.Column(db.Date, nullable=False)
    prioridad = db.Column(db.Enum('alta', 'media', 'baja'), default='media')
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    creador = db.relationship('Usuario', backref='tareas_creadas')
    entregas = db.relationship('Entrega', backref='tarea', lazy=True)

    def __repr__(self):
        return f'<Tarea {self.titulo}>'


class Entrega(db.Model):
    __tablename__ = 'entrega'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tarea.id'), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    archivo_url = db.Column(db.String(500))
    fecha_entrega = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.Enum('pendiente', 'en_revision', 'completada'), default='pendiente')
    calificacion = db.Column(db.Numeric(5, 2))
    comentario_profesor = db.Column(db.Text)

    estudiante = db.relationship('Usuario', backref='entregas')

    def __repr__(self):
        return f'<Entrega tarea={self.tarea_id} est={self.estado}>'


class Cronograma(db.Model):
    __tablename__ = 'cronograma'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_evento = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(50))
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'))
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    creador = db.relationship('Usuario', backref='eventos_cronograma')

    def __repr__(self):
        return f'<Cronograma {self.titulo}>'


class Mensaje(db.Model):
    __tablename__ = 'mensaje'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    remitente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    asunto = db.Column(db.String(255))
    cuerpo = db.Column(db.Text, nullable=False)
    enviado_en = db.Column(db.DateTime, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)
    eliminado_remitente = db.Column(db.Boolean, default=False)
    eliminado_destinatario = db.Column(db.Boolean, default=False)

    remitente = db.relationship('Usuario', foreign_keys=[remitente_id], backref='mensajes_enviados')
    destinatario = db.relationship('Usuario', foreign_keys=[destinatario_id], backref='mensajes_recibidos')


class Recurso(db.Model):
    __tablename__ = 'recurso'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    url_archivo = db.Column(db.String(500))
    tipo = db.Column(db.Enum('documento', 'presentacion', 'enlace', 'video'), nullable=False, default='documento')
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'))
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    creador = db.relationship('Usuario', backref='recursos')

    def __repr__(self):
        return f'<Recurso {self.titulo}>'


class Comunicado(db.Model):
    __tablename__ = 'comunicado'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    publicado_en = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    creador = db.relationship('Usuario', backref='comunicados')


class Grupo(db.Model):
    __tablename__ = 'grupo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    creador = db.relationship('Usuario', backref='grupos_creados')
    miembros = db.relationship('EstudianteGrupo', backref='grupo', lazy=True)


class EstudianteGrupo(db.Model):
    __tablename__ = 'estudiante_grupo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    unido_en = db.Column(db.DateTime, default=datetime.utcnow)

    estudiante = db.relationship('Usuario', backref='grupos_inscritos')