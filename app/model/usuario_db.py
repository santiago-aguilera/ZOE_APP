"""
Modelo SQLAlchemy para USUARIO.
Usa Single Table Inheritance con rol como discriminador.
Mantiene los métodos POO originales.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .db import db


class Usuario(db.Model):
    __tablename__ = "USUARIO"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True)
    contrasena_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)
    periodo_id = Column(Integer, ForeignKey("PERIODO_ACADEMICO.id"), nullable=True)
    creado_en = Column(DateTime, default=datetime.now)
    ultimo_login = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)

    __mapper_args__ = {
        "polymorphic_on": rol,
        "polymorphic_identity": "usuario",
    }

    # Relaciones
    periodo = relationship("PeriodoAcademico", back_populates="usuarios")
    # Mensajes como remitente/destinatario
    mensajes_enviados = relationship(
        "Mensaje", back_populates="remitente",
        foreign_keys="Mensaje.remitente_id", lazy="dynamic"
    )
    mensajes_recibidos = relationship(
        "Mensaje", back_populates="destinatario",
        foreign_keys="Mensaje.destinatario_id", lazy="dynamic"
    )
    # Tareas creadas por este usuario
    tareas_creadas = relationship("Tarea", back_populates="creador", lazy="dynamic")
    # Recursos creados por este usuario
    recursos_creados = relationship("Recurso", back_populates="creador", lazy="dynamic")
    # Comunicados creados por este usuario
    comunicados_creados = relationship("Comunicado", back_populates="creador", lazy="dynamic")
    # Eventos de cronograma creados por este usuario
    eventos_creados = relationship("Cronograma", back_populates="creador", lazy="dynamic")
    # Grupos creados por este usuario
    grupos_creados = relationship("Grupo", back_populates="creador", lazy="dynamic")
    # Relaciones many-to-many a través de tablas intermedias
    profesor_materias = relationship("ProfesorMateria", back_populates="usuario", lazy="dynamic")
    estudiante_materias = relationship("EstudianteMateria", back_populates="usuario", lazy="dynamic")
    estudiante_grupos = relationship("EstudianteGrupo", back_populates="usuario", lazy="dynamic")

    def __init__(self, id=None, nombre=None, correo=None, contrasena_hash=None, rol="usuario", **kwargs):
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        self.nombre = nombre
        self.correo = correo
        self.contrasena_hash = contrasena_hash
        self.rol = rol
        self.activo = True
        self._sesion_activa = False

    @property
    def sesion_activa(self):
        return self._sesion_activa

    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre

    def set_nombre(self, nombre):
        self.nombre = nombre

    def get_correo(self):
        return self.correo

    def set_correo(self, correo):
        self.correo = correo

    def get_rol(self):
        return self.rol

    @staticmethod
    def autenticar(correo, contrasena):
        """
        Método POO estático: valida credenciales contra la BD.
        Retorna la instancia Usuario si las credenciales son válidas, o None.
        SQL: SELECT * FROM USUARIO WHERE correo=? AND contrasena_hash=?
        """
        return Usuario.query.filter_by(
            correo=correo, contrasena_hash=contrasena, activo=True
        ).first()

    def iniciarSesion(self, correo, contrasena_hash):
        if self.correo == correo and self.contrasena_hash == contrasena_hash:
            self._sesion_activa = True
            self.ultimo_login = datetime.now()
            db.session.commit()
            print(f"Sesión iniciada para {self.nombre} ({self.rol})")
        else:
            print("Credenciales incorrectas")

    def cerrarSesion(self):
        if self._sesion_activa:
            self._sesion_activa = False
            print(f"Sesión cerrada para {self.nombre}")
        else:
            print("No hay sesión activa para cerrar")

    def mostrarInfo(self):
        print(f"[{self.rol}] {self.id} - {self.nombre} | {self.correo}")

    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.rol})>"